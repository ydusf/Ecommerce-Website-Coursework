from website import create_app
from website.models import ProductManager

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        ProductManager.add_products_from_database('products.txt', delimiter='| ')
        app.run(debug=True)