from setuptools import setup, find_packages

package_name = "sql_metaparse"
package_version = "0.0.1"
description = long_description = "sql_metaparse"
author = "wrgoldstein"
url = "https://github.com/wrgoldstein/sql-metaparse"


setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author=author,
    url=url,
    packages=find_packages(),
    test_suite='test',
    install_requires=["sqlparse"],
    zip_safe=False,
    python_requires=">=3.6.3",
)
