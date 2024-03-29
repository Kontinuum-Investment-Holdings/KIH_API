import datetime

from setuptools import setup, find_packages

setup(
    name="kih_api",
    version=datetime.datetime.utcnow().strftime("%Y.%m.%d.%H.%M.%S"),
    url="https://github.com/Kontinuum-Investment-Holdings/KIH_API",
    author="Kavindu Athaudha",
    author_email="kavindu@k-ih.co.uk",
    packages=find_packages(where="src", include=["kih_api*"]),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "urllib3",
        "pytz",
        "python-dateutil",
        "pandas",
        "numpy",
        "ibapi",
        "validators",
        "dacite",
        "mongoengine",
        "pymongo",
        "dataclass_csv",
        "openpyxl"
    ]
)
