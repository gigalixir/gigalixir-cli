Tiers & Pricing
~~~~~~~~~~~~~~~

.. _`tiers`:

Tiers
=====

Gigalixir offers 2 tiers of pricing. The free tier is free, but you are limited to 1 instance up to size 0.5 and 1 free tier database. Also, on the free tier, if you haven't deployed anything for over 30 days, we will send you an email to remind you to keep your account active. If you do not, your app may be scaled down to 0 replicas. We know this isn't ideal, but we think it is better than sleeping instances and we appreciate your understanding since the free tier does cost a lot to run.

=======================  ========= =============
Instance Feature         FREE Tier STANDARD Tier
=======================  ========= =============
Zero-downtime deploys    YES       YES
Websockets               YES       YES
Automatic TLS            YES       YES
Log Aggregation          YES       YES
Log Tailing              YES       YES
Hot Upgrades             YES       YES
Remote Observer          YES       YES
No Connection Limits     YES       YES
No Daily Restarts        YES       YES
Custom Domains           YES       YES
Postgres-as-a-Service    YES       YES
SSH Access               YES       YES
Vertical Scaling                   YES
Horizontal Scaling                 YES
Clustering                         YES
Multiple Apps                      YES
Team Permissions                   YES
No Inactivity Checks               YES
=======================  ========= =============

========================  ========= =============
Database Feature          FREE Tier STANDARD Tier
========================  ========= =============
SSL Connections           YES       YES
Data Import/Export        YES       YES
Data Encryption                     YES
Dedicated CPU                       YES*
Dedicated Memory                    YES
Dedicated Disk                      YES
No Connection Limits                YES*
No Row Limits                       YES
Backups                             YES
Scalable/Upgradeable                YES
Automatic Data Migration            YES
Extensions                          YES
Functions                           YES
Triggers                            YES
Role Management                     YES
========================  ========= =============

* Only size 4 and above have dedicated CPU. See :ref:`database sizes`.
* Databases still have connection limits based on Google Cloud SQL limits. See https://cloud.google.com/sql/docs/postgres/quotas#fixed-limits

.. _`gigalixir heroku feature comparison`:

Gigalixir vs Heroku Feature Comparison
======================================

=======================  =================== ======================= =========== =============== ==================
Feature                  Gigalixir FREE Tier Gigalixir STANDARD Tier Heroku Free Heroku Standard Heroku Performance
=======================  =================== ======================= =========== =============== ==================
Websockets               YES                 YES                     YES         YES             YES
Log Aggregation          YES                 YES                     YES         YES             YES
Log Tailing              YES                 YES                     YES         YES             YES
Custom Domains           YES                 YES                     YES         YES             YES
Postgres-as-a-Service    YES                 YES                     YES         YES             YES
No sleeping              YES                 YES                                 YES             YES
Automatic TLS            YES                 YES                                 YES             YES
Preboot                  YES                 YES                                 YES             YES
Zero-downtime deploys    YES                 YES
SSH Access               YES                 YES
Hot Upgrades             YES                 YES
Remote Observer          YES                 YES
No Connection Limits     YES                 YES
No Daily Restarts        YES                 YES
Flexible Instance Sizes                      YES
Clustering                                   YES
Horizontal Scaling                           YES                                 YES             YES
Built-in Metrics                                                                 YES             YES
Threshold Alerts                                                                 YES             YES
Dedicated Instances                                                                              YES
Autoscaling                                                                                      YES
=======================  =================== ======================= =========== =============== ==================

.. _`pricing`:

Pricing Details
===============

In the free tier, everything is no-credit-card free. Once you upgrade to the standard tier, you pay $10 for every 200MB of memory per month. CPU, bandwidth, and power are free.

See our `cost estimator <https://gigalixir.com/pricing>`_ to calculate how much you should expect to pay each month. Keep reading for exactly how we compute your bill.

Every month after you sign up on the same day of the month, we calculate the number of replica-size-seconds used, multiply that by $0.00001866786, and charge your credit card.

replica-size-seconds is how many replicas you ran multiplied by the size of each replica multiplied by how many seconds they were run. This is aggregated across all your apps and is prorated to the second.

For example, if you ran a single 0.5 size replica for 31 days, you will have used

.. code-block:: bash

  (1 replica) * (0.5 size) * (31 days) = 1339200 replica-size-seconds.

Your monthly bill will be

.. code-block:: bash

  1339200 * $0.00001866786 = $25.00.

If you ran a 1.0 size replica for 10 days, then scaled it up to 3 replicas, then 10 days later scaled the size up to 2.0 and it was a 30-day month, then your usage would be

.. code-block:: bash

  (1 replica) * (1.0 size) * (10 days) + (3 replicas) * (1.0 size) * (10 days) + (3 replicas) * (2.0 size) * (10 days) = 8640000 replica-size-seconds

Your monthly bill will be

.. code-block:: bash

  8640000 * $0.00001866786 = $161.29.

For database pricing, see :ref:`database sizes`.

.. _`database sizes`:

Database Sizes & Pricing
========================

In the free tier, the database is free, but it is really not suitable for production use. It is a multi-tenant postgres database cluster with shared CPU, memory, and disk. You are limited to 2 connections, 10,000 rows, and no backups. Idle connections are terminated after 5 minutes. If you want to upgrade your database, you'll have to migrate the data yourself. For a complete feature comparison see :ref:`tiers`.

In the standard tier, database sizes are defined as a single number for simplicity. The number defines how many GBs of memory your database will have. Supported sizes include 0.6, 1.7, 4, 8, 16, 32, 64, and 128. Sizes 0.6 and 1.7 share CPU with other databases. All other sizes have dedicated CPU, 1 CPU for every 4 GB of memory. For example, size 4 has 1 dedicated CPU and size 64 has 16 dedicated CPUs. All databases start with 10 GB disk and increase automatically as needed.

====  ============= ======= ============= ================ =============
Size  Price / Month RAM     Rollback Days Connection Limit Storage Limit
====  ============= ======= ============= ================ =============
0.6   $25           0.6 GB  7             25               25 GB
1.7   $50           1.7 GB  7             50               50 GB
  4   $100          4 GB    7             100              100 GB
  8   $200          8 GB    7             200              200 GB
 16   $400          16 GB   7             250              400 GB
 32   $800          32 GB   7             300              800 GB
 64   $1600         64 GB   7             400              1.6 TB
128   $3200         128 GB  7             500              3.2 TB
====  ============= ======= ============= ================ =============

Prices are prorated to the second.

For more, see :ref:`provisioning database` and :ref:`provisioning free database`.

.. _`replica sizing`:

Replica Sizing
==============

  - A replica is a docker container that your app runs in.
  - Replica sizes are available in increments of 0.1 between 0.2 and 384, but for the higher sizes you'll need to :ref:`contact us<help>` first.
  - 1 size unit is 1GB memory, 1 CPU share, and 564mbps egress bandwidth.
  - 1 CPU share is 200m as defined using `Kubernetes CPU requests`_ or roughly 20% of a core guaranteed.

    - If you are on a machine with other containers that don't use much CPU, you can use as much CPU as you like.

  - Memory is defined using `Kuberenetes memory requests`_.

    - If you are on a machine with other machines that don't use much memory, you can use as much memory as you like.

  - Memory and CPU sizes can not be adjusted separately.

.. _`Kubernetes CPU requests`: https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-cpu
.. _`Kuberenetes memory requests`: https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-memory

Why was my app scaled down to 0?
================================

On the free tier apps are scaled down to 0 if there have been no deploys for 30 days. We send a warning email after 23 days. To prevent this from happening, make sure you either deploy often or upgrade to the standard tier.

.. _`custom domain pricing`:

Custom Domain Pricing
=====================

Gigalixir allows custom domains for each application.  Up to 100 custom domains are included free for each application.  Additional custom domains can be purchased by :ref:`contacting us<help>` and are priced according to the following schedule.

========  =============
Quantity  Price / Month
========  =============
     100  FREE
   1,000  $15
   5,000  $60
  10,000  $100
========  =============

After 10,000 it becomes $100 per month for each 10,000 domain block.



Limits
======

Gigalixir is designed for Elixir/Phoenix apps and it is common for Elixir/Phoenix apps to have many connections open at a time and to have connections open for long periods of time. Because of this, we do not limit the number of concurrent connections or the duration of each connection[1][2].

We also know that Elixir/Phoenix apps are designed to be long-lived and potentially store state in-memory so we do not restart replicas arbitrarily. In fact, replicas should not restart at all, unless there is an extenuating circumstance that requires it.  For apps that require extreme high availability, we suggest that your app be able to handle node restarts just as you would for any app not running on Gigalixir.

That said, we do have a number of limits in order to prevent abuse which are listed below. If you need to request a higher limit, :ref:`contact us<help>` and we'll do our best to accomodate you.

============= ======
Resource      Limit
============= ======
Log Drains    5
Apps          100
SSH Keys      50
Collaborators 25
Config Vars   32kb
Slug Size     500mb
Repo Size     1gb
Build Time    30m
Disk          10gb
Bandwidth     1tb/mo
============= ======

[1] Because Gigalixir runs on Google Compute Engine, you may bump into an issue with connections that stay idle for 10m. For more information and how to work around it, see https://cloud.google.com/compute/docs/troubleshooting
[2] We do have a timeout of 60 minutes for connections after an nginx configuration reload. If you have a long-lived websocket connection and our nginx configuration is reloaded, the connection will be dropped 60 minutes later. Unfortunately, nginx reloads happen frequently under Kubernetes.

