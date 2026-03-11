"""
Product Routes - DynamoDB Version
Handles product browsing and admin product management
"""

import os
import uuid
import math
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.product_model import Product
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

product_bp = Blueprint("product", __name__)

# ── Upload config ─────────────────────────────────────────────────
UPLOAD_FOLDER  = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file):
    if file and file.filename and allowed_file(file.filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, unique_name))
        return f"/static/images/uploads/{unique_name}"
    return None

# ── Admin decorator ───────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", lambda: False)():
            flash("Admin access required.", "danger")
            return redirect(url_for("product.index"))
        return f(*args, **kwargs)
    return decorated

# ── Customer Routes ───────────────────────────────────────────────

@product_bp.route("/")
def index():
    search  = request.args.get("search", "").strip()
    page    = int(request.args.get("page", 1))
    per_page = 9

    if search:
        all_products = Product.search_products(search)
    else:
        all_products = Product.get_all_products()

    # Sort by created_at descending
    all_products.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    total       = len(all_products)
    total_pages = max(1, math.ceil(total / per_page))
    start       = (page - 1) * per_page
    products    = all_products[start: start + per_page]

    pagination = {
        "page":     page,
        "pages":    total_pages,
        "total":    total,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_num": page - 1,
        "next_num": page + 1,
    }

    return render_template("product/index.html",
                           products=products,
                           pagination=pagination,
                           search=search)


@product_bp.route("/product/<product_id>")
def detail(product_id):
    product = Product.find_by_id(product_id)
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("product.index"))

    # Related products — all except current
    all_products = Product.get_all_products()
    related = [p for p in all_products if p.get("product_id") != product_id][:3]

    return render_template("product/detail.html", product=product, related=related)


# ── Admin Routes ──────────────────────────────────────────────────

@product_bp.route("/admin/products")
@login_required
@admin_required
def admin_products():
    products = Product.get_all_products()
    products.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return render_template("product/admin_products.html", products=products)


@product_bp.route("/admin/product/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price       = request.form.get("price", "").strip()
        stock       = request.form.get("stock", "0").strip()
        image_url   = request.form.get("image_url", "").strip()

        errors = []
        if not name:
            errors.append("Product name is required.")
        elif any(p["name"] == name for p in Product.get_all_products()):
            errors.append("A product with this name already exists.")
        if not description:
            errors.append("Description is required.")
        try:
            price = float(price)
            if price < 0:
                errors.append("Price must be positive.")
        except ValueError:
            errors.append("Price must be a valid number.")
        try:
            stock = int(stock)
            if stock < 0:
                errors.append("Stock must be positive.")
        except ValueError:
            errors.append("Stock must be a valid number.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("product/add_product.html")

        uploaded_file  = request.files.get("image_file")
        final_image_url = save_uploaded_image(uploaded_file) or image_url or "/static/images/default-product.jpg"

        Product.create_product(name=name, price=price, description=description,
                                stock=stock, image_url=final_image_url)
        flash(f'Product "{name}" added successfully!', "success")
        return redirect(url_for("product.admin_products"))

    return render_template("product/add_product.html")


@product_bp.route("/admin/product/<product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.find_by_id(product_id)
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("product.admin_products"))

    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price       = request.form.get("price", "").strip()
        stock       = request.form.get("stock", "0").strip()
        image_url   = request.form.get("image_url", "").strip()

        errors = []
        try:
            price = float(price)
        except ValueError:
            errors.append("Price must be a valid number.")
        try:
            stock = int(stock)
        except ValueError:
            errors.append("Stock must be a valid number.")

        all_products = Product.get_all_products()
        existing = next((p for p in all_products if p["name"] == name and p["product_id"] != product_id), None)
        if existing:
            errors.append("Another product with this name already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("product/edit_product.html", product=product)

        uploaded_file   = request.files.get("image_file")
        final_image_url = save_uploaded_image(uploaded_file) or image_url or product.get("image_url", "/static/images/default-product.jpg")

        Product.update_product(product_id, {
            "name":        name,
            "description": description,
            "price":       price,
            "stock":       stock,
            "image_url":   final_image_url,
            "updated_at":  datetime.utcnow()
        })

        flash(f'Product "{name}" updated successfully!', "success")
        return redirect(url_for("product.admin_products"))

    return render_template("product/edit_product.html", product=product)


@product_bp.route("/admin/product/<product_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.find_by_id(product_id)
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for("product.admin_products"))

    Product.delete_product(product_id)
    flash(f'Product "{product["name"]}" deleted.', "success")
    return redirect(url_for("product.admin_products"))
