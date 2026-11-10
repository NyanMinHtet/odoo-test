# Custom Hello addon manifest
name = "Custom Hello"
version = "17.0.1.0.0"
depends = ["base"]
data = [
    "security/ir.model.access.csv",
    "views/hello_views.xml",
]
installable = True
application = True
license = "LGPL-3"
