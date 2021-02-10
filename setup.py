from setuptools import setup, find_namespace_packages

package_name = "bbt"
package_version = "0.0.1"
description = long_description = "bbt"
author = "better"
author_email = "wgoldstein@better.com"
url = "github.com/better"


setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author="Fishtown Analytics",
    author_email="info@fishtownanalytics.com",
    url="https://github.com/fishtown-analytics/dbt",
    # packages=find_namespace_packages(include=['dbt', 'dbt.*']),
    packages=["lib"],
    package_data={},
    test_suite='test',
    entry_points={},
    scripts=[
        'scripts/bbt',
    ],
    install_requires=["sqlparse"],
    zip_safe=False,
    python_requires=">=3.6.3",
)
