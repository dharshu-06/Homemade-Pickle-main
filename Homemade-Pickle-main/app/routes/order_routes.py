"""
Order Routes - DynamoDB Version
Handles shopping cart, checkout, and order history
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models.product_model import Product
from app.models.order_model import Order
from datetime import datetime

order_bp = Blueprint('order', __name__)


def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart
    session.modified = True


# ── Cart Routes ───────────────────────────────────────────────────

@order_bp.route('/add-to-cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):

    product = Product.find_by_id(product_id)
    if not product:
        flash("Product not found", "danger")
        return redirect(url_for('product.index'))

    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        quantity = 1

    if quantity < 1:
        flash("Quantity must be at least 1", "danger")
        return redirect(url_for('product.index'))

    if quantity > product.get("stock", 0):
        flash(f"Only {product.get('stock', 0)} items available", "danger")
        return redirect(url_for('product.index'))

    cart = get_cart()
    pid  = product["product_id"]

    if pid in cart:
        cart[pid]["quantity"] += quantity
    else:
        cart[pid] = {
            "product_id": pid,
            "name":       product["name"],
            "price":      product["price"],
            "quantity":   quantity,
            "image_url":  product.get("image_url")
        }

    save_cart(cart)
    flash(f"Added {quantity} x {product['name']} to cart!", "success")
    return redirect(url_for('product.index'))


@order_bp.route('/cart')
def view_cart():

    cart       = get_cart()
    cart_items = []
    total      = 0

    for pid, item in cart.items():
        product = Product.find_by_id(pid)
        if product:
            subtotal = product["price"] * item["quantity"]
            cart_items.append({
                "product_id": pid,
                "name":       product["name"],
                "price":      product["price"],
                "quantity":   item["quantity"],
                "subtotal":   subtotal,
                "image_url":  product.get("image_url")
            })
            total += subtotal

    return render_template("order/cart.html", cart_items=cart_items, total=total)


@order_bp.route('/cart/remove/<product_id>')
def remove_from_cart(product_id):
    cart = get_cart()
    if product_id in cart:
        del cart[product_id]
        save_cart(cart)
        flash("Item removed from cart", "success")
    else:
        flash("Item not found in cart", "warning")
    return redirect(url_for("order.view_cart"))


@order_bp.route('/cart/update', methods=['POST'])
def update_cart():
    cart = get_cart()
    for pid in list(cart.keys()):
        qty = request.form.get(f"quantity_{pid}")
        if qty is not None:
            try:
                qty = int(qty)
                if qty <= 0:
                    del cart[pid]
                else:
                    cart[pid]["quantity"] = qty
            except ValueError:
                flash("Invalid quantity input", "warning")
    save_cart(cart)
    flash("Cart updated", "success")
    return redirect(url_for("order.view_cart"))


# ── Checkout ──────────────────────────────────────────────────────

@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():

    cart = get_cart()
    if not cart:
        flash("Your cart is empty", "warning")
        return redirect(url_for("product.index"))

    cart_items = []
    subtotal   = 0

    for pid, item in cart.items():
        product = Product.find_by_id(pid)
        if product:
            line_total = product["price"] * item["quantity"]
            cart_items.append({
                "product_id": pid,
                "name":       product["name"],
                "price":      product["price"],
                "quantity":   item["quantity"],
                "subtotal":   line_total,
                "image_url":  product.get("image_url")
            })
            subtotal += line_total

    tax   = round(subtotal * 0.10, 2)
    total = round(subtotal + tax, 2)

    if request.method == "POST":
        order_items = []

        for pid, item in cart.items():
            product = Product.find_by_id(pid)
            if not product:
                flash("Product not available", "danger")
                return redirect(url_for("order.view_cart"))

            quantity = item["quantity"]
            if quantity > product.get("stock", 0):
                flash(f"Only {product['stock']} items available for {product['name']}", "danger")
                return redirect(url_for("order.view_cart"))

            order_items.append({
                "product_id": pid,
                "name":       str(product["name"]),
                "price":      float(product["price"]),
                "quantity":   int(quantity),
                "subtotal":   float(product["price"] * quantity)
            })

            # Deduct stock in DynamoDB
            Product.deduct_stock(pid, quantity)

        # Save order in DynamoDB
        order_id = Order.create_order(
            user_id=str(current_user.id),
            order_items=order_items,
            total_amount=float(total)
        )

        session["cart"] = {}
        session.modified = True

        flash(f"Order placed successfully! Order ID: {order_id}", "success")
        return redirect(url_for("order.order_history"))

    return render_template("order/checkout.html",
                           cart_items=cart_items,
                           subtotal=subtotal,
                           tax=tax,
                           total=total)


# ── Order History ─────────────────────────────────────────────────

@order_bp.route('/history')
@login_required
def order_history():
    orders = Order.find_by_user(str(current_user.id))
    return render_template("order/history.html", orders=orders)


@order_bp.route('/order/<order_id>')
@login_required
def order_detail(order_id):
    order = Order.find_by_id(order_id)

    if not order:
        flash("Order not found", "danger")
        return redirect(url_for("order.order_history"))

    if order["user_id"] != str(current_user.id):
        flash("You do not have permission to view this order", "danger")
        return redirect(url_for("order.order_history"))

    return render_template("order/detail.html", order=order)
