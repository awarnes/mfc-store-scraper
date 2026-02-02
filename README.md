# MFC Store Scraper

Rather than doing the manual work of adding each product to our Shopify store individually, this scraping software will help us upload products in batches as well as keep track of which products are available for purchase and which are not.

Currently, we use the CSV upload option to bulk upload products into our Shopfiy store. More information can be found here along with a template CSV file: [Using CSV files](https://help.shopify.com/en/manual/products/import-export/using-csv)

Previously, we supported scraping for the [Hummingbird Wholesale](https://hummingbirdwholesale.com) site. That code has been moved to the [archive/hummingbird](./archive/hummingbird) folder. Going forward we'll primarily support Azure Standard and possibly others going forward.

## Using the repo

### Pre-requisites
- [uv](https://docs.astral.sh/uv/)
- [docker](https://www.docker.com/products/docker-desktop/)

Optionally, you can use a database UI like [dbeaver](https://dbeaver.io/download/).

### Getting started locally
1. Run `uv sync` to install dependencies
2. Create a local environment file with `cp .env.example .env.local`
3. Start up your local docker daemon
4. Run `docker compose up -d` to start up the local database
5. You should now see the volume and container created. You can verify things are running by checking in the Docker Desktop app or by running `docker compose ps` and verifying that the `azure-db` service is running.

Setting up `dbeaver`:
1. Create a new PostgreSQL connection
2. Set the Host to `localhost`
3. Set the Port to `5999`
4. Set the Database to `azure`
5. Set the Username to `root`
6. Set the Password to `localpassword` (or whatever you have set in the `.env.local` file)

### Running the scraper
1. Run `uv run main.py`
2. Verify that the scraper completes by checking the databse in DBeaver or similar access



> In order to update new prices, run the script and when uploading select the `Overwrite any current products...` check box. This will ensure that new prices overwrite old prices.

## Collaborate

Send a request to `@awarnes` in Slack to get access to contribute to this repository.

Please feel free to update anything you see fit and create a pull request on [GitHub](https://github.com/awarnes/mfc-store-scraper) with anything you'd like to change.

Don't forget to update any documentation and write any tests that are affected by your changes.

We use pylint to check each pull request and make sure everything is in line with standard styles. You will need to lint and fix anything that doesn't pass the check before you can merge your PR. Feel free to run the check below before pushing to your branch so that you're ready to go when you make your PR.

### Lint repo with pylint:
```bash
uv run pylint ./src
```

### Running tests:
[[[UNDER CONSTRUCTION]]]
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
[[[UNDER CONSTRUCTION]]]
```bash
python -m unittest discover -s tests/integration
```
