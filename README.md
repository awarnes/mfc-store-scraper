# MFC Store Scraper

Rather than doing the manual work of adding each product to our shopify store individually, this scraping software will help us upload products in batches as well as keep track of which products are available for purchase and which are not.

Currently, we use the CSV upload option to bulk upload products into our Shopfiy store. More information can be found here along with a template CSV file: [Using CSV files](https://help.shopify.com/en/manual/products/import-export/using-csv)

Currently, we only support scraping for the Hummingbird Wholesale site at this time.

## Run

Run the [main.py](./main.py) script to pull all product information from Hummingbird Wholesale, save it to a file, and then format the data into a CSV for upload into the Shopify store.

## Collaborate

Please feel free to update anything you see fit and create a pull request on [GitHub](https://github.com/awarnes/mfc-store-scraper) with anything you'd like to change.

Don't forget to update any documentation and write any tests that are affected by your changes.

Check pylint:
```bash
pylint $(find . -name "*.py" | xargs)
```

## Future
Future development projects/ideas:
* [ ] Write full unit and integration tests for system so we know when something changes in a bad way
* [ ] Make use of the Shopify [GraphQL Admin API](https://shopify.dev/api/usage/bulk-operations/imports) to automate the import process rather than generating a CSV
* [ ] Genericize features/functionality to allow us to wrap/import from any wholesaler partner
* [ ] Connect to [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html) and expand functionality so that we can run it on a schedule to validate product availability
