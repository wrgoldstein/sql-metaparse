from setuptools import setup, find_namespace_packages

package_name = "bbt"
package_version = "0.0.1"
description = long_description = "bbt"
author = "wrgoldstein"
url = "https://github.com/wrgoldstein/sql-metaparse"


setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author=author,
    url=url,
    packages=["lib"],
    package_data={},
    test_suite='test',
    entry_points={},
    install_requires=["sqlparse"],
    zip_safe=False,
    python_requires=">=3.6.3",
)
