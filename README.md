# wyre-invoicing-api

## Usage

Simplest and quickest way to get running is to use Docker.

Run the services:

    docker-compose up

After invoice accounts have been sent payments and you want to drain the invoice accounts to another wallet:

    docker-compose exec api widrain --json-rpc http://ganache:8545/ [dest_address]

## API Requests

### Get All Invoices

    curl http://localhost:8000/invoice

### Get A Specific Invoices

    curl http://localhost:8000/invoice/[invoice_id]

### Add an Invoice

    curl -X POST -H 'Content-Type: application/json'  -d '{"total": 210000000000000}' http://localhost:8000/invoice
