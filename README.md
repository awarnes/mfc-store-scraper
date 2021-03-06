# MFC Store Scraper

Rather than doing the manual work of adding each product to our Shopify store individually, this scraping software will help us upload products in batches as well as keep track of which products are available for purchase and which are not.

Currently, we use the CSV upload option to bulk upload products into our Shopfiy store. More information can be found here along with a template CSV file: [Using CSV files](https://help.shopify.com/en/manual/products/import-export/using-csv)

Currently, we only support scraping for the [Hummingbird Wholesale](https://hummingbirdwholesale.com) site at this time.

## Run

Run the [main.py](./main.py) script to pull all product information from Hummingbird Wholesale, save it to a file, and then format the data into a CSV for upload into the Shopify store.

> Note: be sure to have Python 3.8+ installed to run the program

1. `pip install -r requirements.txt`
1. `python3 ./main.py`
1. On the Shopify products page, click the `Import` button in the top right, and select the `outputs/hummingbird_products.csv` file.

> In order to update new prices, run the script and when uploading select the `Overwrite any current products...` check box. This will ensure that new prices overwrite old prices.

## Collaborate

Send a request to `@awarnes` in Slack to get access to contribute to this repository.

Please feel free to update anything you see fit and create a pull request on [GitHub](https://github.com/awarnes/mfc-store-scraper) with anything you'd like to change.

Don't forget to update any documentation and write any tests that are affected by your changes.

We use pylint to check each pull request and make sure everything is in line with standard styles. You will need to lint and fix anything that doesn't pass the check before you can merge your PR. Feel free to run the check below before pushing to your branch so that you're ready to go when you make your PR.

### Lint repo with pylint:
```bash
pylint $(find . -name "*.py" | xargs)
```

### Running tests:
Tests are written using the [unittest](https://docs.python.org/3/library/unittest.html) builtin library.

To run all tests for the project:
```bash
python -m unittest discover -s tests
```
#### Unit tests
```bash
python -m unittest discover -s tests/unit
```

#### Integration tests
```bash
python -m unittest discover -s tests/integration
```

## Future
Future development projects/ideas:
* [ ] Write full unit and integration tests for system so we know when something changes in a bad way
* [ ] Make use of the Shopify [GraphQL Admin API](https://shopify.dev/api/usage/bulk-operations/imports) to automate the import process rather than generating a CSV
* [x] Genericize features/functionality to allow us to wrap/import from any wholesaler partner
* [ ] Connect to [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html) and expand functionality so that we can run it on a schedule to validate product availability
