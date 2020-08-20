Domains
~~~~~~~

.. _`custom domains`:

How to Set Up a Custom Domain
=============================

After your first deploy, you can see your app by visiting https://$APP_NAME.gigalixirapp.com/, but if you want, you can point your own domain such as www.example.com to your app. To do this, run the following command and follow the instructions.

.. code-block:: bash

    gigalixir domains:add www.example.com

This will do a few things. It registers your fully qualified domain name in the load balancer so that it knows to direct traffic to your containers. It also sets up SSL/TLS encryption for you and provisions a certificate. For more information on how SSL/TLS works, see :ref:`how-tls-works`.

.. important::

    If you want both the apex domain and a subdomain such as www, be sure to run `gigalixir domains:add` for each one.

.. note::

    Per the RFC spec, many DNS providers (such as GoDaddy and AWS Route 53) do not allow CNAME records for apex domains. If you are using a DNS provider that supports ALIAS records (such as Namecheap), you may define an ALIAS record for your apex domain that points to your corresponding gigalixir DNS domain, e.g. `example.com.gigalixirdns.com.`. Alternatively, you can use a redirect service such as redirect.pizza to securely forward requests for your apex domain to your `www.` sub-domain.

.. note::

    If you need a wildcard domain, feel free to :ref:`contact us<help>` and we can help you get set up, but you will have to provide your own wildcard certificate.

.. note::

    You may need to change your :elixir:`check_origin` setting in order for websockets to pass the origin check. See https://hexdocs.pm/phoenix/Phoenix.Endpoint.html#module-runtime-configuration

How to Set Up SSL/TLS
=====================

SSL/TLS certificates are set up for you automatically assuming your custom domain is set up properly.  Note that your application will continue to be served on http as well as https.  If you want to force your users to use https by redirecting any http requests, specify that in your `config/prod.exs`:

.. code-block:: elixir

    config :my_app, MyAppWeb.Endpoint,
       force_ssl: [rewrite_on: [:x_forwarded_proto]]

This configures your app to `check the x-forwarded-proto header`_ set by Gigalixir, and redirect to https, if appropriate.

For more information on how this works internally, see :ref:`how-tls-works`.

.. _`check the x-forwarded-proto header`: https://hexdocs.pm/plug/Plug.SSL.html#module-x-forwarded-proto
