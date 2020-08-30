# encoding: utf-8
#
# Wrapper for interacting with Azure Blob Storage
# Copyright (c) 2020 Klaus K. Holst.  All rights reserved.
#

import pandas as pd
import os
from io import StringIO, BytesIO
from azure.storage.blob import BlobServiceClient
import azure.core as az
from .__utils__ import filesize # noqa F403
# import pyarrow.parquet as pq


class BlobStorage:
    """Simple class for reading and writing files on Azure Blob Storage

    The connection string can either be given at the class
    initialization or alternatively it will be read from the
    environment variable AZURE_STORAGE_CONNECTION_STRING
    """
    blobservice = None
    container = None
    container_name = ""

    def __init__(self, container_str, connect_str=None):
        """Class initialization

        Examples
        --------
        import kvaser
        blob = kvaser.BlobStorage('my-kvaser-test')
        df = kvaser.getdata() # A test pandas dataframe
        blob.write_pq(df, 'a.pq')
        {'etag': '"0x8D84D076069EDBB"', 'last_modified': datetime.datetime(2020, 8, 30, 17 ...
        blob.read_pq('a.pq')
        blob.write_csv(df, 'a.csv')
        blob.list()
        blob.read_csv('a.csv')

        Parameters
        ----------
        container_str: str
            Name of container to use
        connect_str: str
            Connection string
        Returns
        -------
        BlobStorage
            BlobStorage object
        """
        if connect_str is None:
            connect_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        self.blobservice = BlobServiceClient.from_connection_string(connect_str)
        if container_str is None:
            self.blobservice.list_containers().next
        self.container(container_str)

    def container(self, name):
        """Switch container.

        A new container will be created if the specified one does not yet exists.

        Parameters
        ----------
        name: str
            Name of container
        """
        self.container_name = name
        self.container = self.blobservice.get_container_client(name)
        try:
            self.container.get_container_properties()
        except az.exceptions.ResourceNotFoundError:
            self.container = self.container.create_container()

    def list(self):
        """List blobs in the container
        """
        for x in self.container.list_blobs():
            sz = filesize(x.size)
            print(x.name + '\t' + str(sz[0]) + ' ' + sz[1])

    def list_container(self):
        """List all containers
        """
        for x in self.blobservice.list_containers():
            print(x.name)

    def read_pq(self, file):
        """Read parquet file from blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        dl = blob_client.download_blob()
        df = pd.read_parquet(BytesIO(dl.content_as_bytes()))
        return df

    def write_pq(self, df, file):
        """Write pandas dataframe to parquet file on blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        buf = BytesIO()
        try:
            df.to_parquet(buf, index=False)
            val = blob_client.upload_blob(buf.getvalue(), blob_type='BlockBlob', overwrite=True)
        finally:
            buf.close()
        return val

    def read_csv(self, file):
        """Read csv file from blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        dl = blob_client.download_blob()
        df = pd.read_csv(StringIO(dl.content_as_text()))
        return df

    def write_csv(self, df, file):
        """Write pandas dataframe to csv file on blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        output = df.to_csv(index=False, encoding='utf-8')
        return blob_client.upload_blob(output, blob_type='BlockBlob', overwrite=True)

    def delete(self, file):
        """Delete object (file) from blob storage
        """
        blob_client = self.blobservice.get_blob_client(container=self.container_name, blob=file)
        try:
            blob_client.delete_blob()
        except az.exceptions.ResourceNotFoundError:
            pass

    def delete_container(self, name=None):
        """Delete container
        """
        if name is None:
            name = self.container_name
        self.blobservice.delete_container(name)
