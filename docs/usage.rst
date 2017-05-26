=====
Usage
=====

To be able to use asyncOrm you have to provide database, the loop and the modules where the models are defined.
For that we provide a **configure_orm** function that will return the already configured orm you will use on the whole application

.. code-block:: python

    from asyncorm import configure_orm

    db_config = {'database': 'sanic_example',
                 'host': 'localhost',
                 'user': 'ormdbuser',
                 'password': 'ormDbPass',
                 }

    orm_app = configure_orm({'loop': loop,  # always use the sanic loop!
                             'db_config': db_config,
                             'modules': ['library', ],  # list of apps
                             })

**AsyncOrm should be configured once and only once in every project**, and preferibly before everything really starts. Also make sure that the async loop is be the same your application uses.

Thats all!
As you can see its very simple to configure asyncOrm, as long as you provide the needed information, asyncOrm will take care of inspecting the modules and detect all the models declared inside them.
So you can then retrieve them both with direct imports or using the provided convenience **get_model** function (recomended):

.. code-block:: python

    from asyncorm import get_model

    Book = get_model('Book')
    # or
    Author = get_model('app.Author')

Understand that all the magic on the ORM is made behind scenes, in fact that function is just a wrapper around the method existent in the ORM. Most of the times you will not need to act on the ORM after the basic configuration.

Please find the `full example`_ for sanic that you will find in the repository, so you can see how easy it is to work with asyncOrm.

.. _`full example`: https://pip.pypa.io
