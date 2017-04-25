# -*- coding: utf-8 -*-
import abc


class AbstractParser(metaclass=abc.ABCMeta):

    @abc.abstractclassmethod
    def parse(self, resp):
        raise NotImplementedError


class RawParser(AbstractParser):
    """A class that returns a response object as is
    
    It is a class that returns the response object as it is.
    Mainly use it for testing and debugging purposes.

    """
    @classmethod
    def parse(cls, resp):
        """Parse response
        
        :param resp: requests's response object
        :return: requests's response object

        """
        return resp


class JsonParser(AbstractParser):
    """converts a response object to JSON and returns it"""
    @classmethod
    def parse(cls, resp):
        """Parse response
        
        :param resp: requests's response object
        :return: `response.json()`

        """
        return resp.json()
