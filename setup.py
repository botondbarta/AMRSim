from setuptools import setup

setup(
    name='amrsim',
    version='0.1',
    description='',
    url='',
    packages=['amrsim'],
    license='',
    author='',
    python_requires='',
    install_requires=[
        'setuptools~=69.5.1',
        'amrlib==0.8.0',
        'numpy==1.26.4',
        'pandas==2.2.2',
        'penman==1.3.0',
        'torch==1.12.0',
        'torch_geometric==2.1.0',
        'torch_sparse==0.6.15',
        'transformers==4.24.0',
        'networkx==2.6.3',
        'unidecode==1.3.6',
        'nltk==3.7',
        'torch_scatter==2.0.9',
    ]
)