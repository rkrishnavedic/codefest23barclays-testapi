import json
import os
import stripe
import logging
import azure.functions as func

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

@app.route(route="donate")
def donate(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        print(req_body)

        # Extract amount and currency from the request body
        amount = req_body.get('amount', 1000)  # Default amount is 1000
        currency = req_body.get('currency', 'inr')  # Default currency is INR

        # Get the 'referer' header or provide a default URL
        referer = req.headers.get('Referer', 'http://localhost:7071/api/http_trigger')

        # Create a Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'Donation',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=referer + '?success=true',
            cancel_url=referer + '?canceled=true',
        )

        print(session)

        return func.HttpResponse(
            json.dumps({'sessionId': session.id, 'sessionUrl':session.url}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            f"Internal Server Error: {str(e)}",
            status_code=500
        )