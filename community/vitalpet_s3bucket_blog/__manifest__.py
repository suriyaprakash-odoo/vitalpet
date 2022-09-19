# -*- coding: utf-8 -*-
{
    "name": """Odoo S3 Bucket Storage""",
    "summary": """Odoo S3 Bucket Storage""",
    "category": "Tools",
    "images": [],
    "version": "10.0.0",
    "application": False,

    "author": "Esousy",

    "depends": ['vitalpet_promote', 'hr'
    ],
    "external_dependencies": {"python": ['boto3'], "bin": []},
    "data": [
        "views/ir_attachment_s3.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
