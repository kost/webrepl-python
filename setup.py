import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webrepl",
    version="0.1.0",
    author="Vlatko Kosturjak",
    author_email="vlatko.kosturjak@gmail.com",
    description="Handle micropython web_repl",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kost/webrepl-python",
    packages=setuptools.find_packages(),
    py_modules=['webrepl'],
    install_requires=[
      "",
    ],
    classifiers=[
      "Programming Language :: Python :: 2",
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ],
    scripts=[
      'scripts/webreplcmd'
    ]
)

