from doct import Document
import ujson
import time as ttime
from amostra.client import conf
from uuid import uuid4
from os.path import expanduser
import mongoquery
from .amutils import doc_or_uid_to_uid


def _find_local(fname, qparams, as_doct=False):
    """Find a document created using the local framework
    Parameters
    -----------
    fname: str
        Name of the query should be run
    qparams: dict
        Query parameters. Similar to online query methods

    Yields
    ------------
    c: doct.Document, StopIteration
        Result of the query if found

    """
    res_list = []
    try:
        with open(fname, 'r') as fp:
            local_payload = ujson.load(fp)
        qobj = mongoquery.Query(qparams)
        for i in local_payload:
            if qobj.match(i):
                res_list.append(i)
    except FileNotFoundError:
        raise RuntimeWarning('Local file {} does not exist'.format(fname))
    if as_doct:
        for c in res_list:
            yield Document(fname.split('.')[0], c)
    else:
        for c in res_list:
            yield c


def _update_local(fname, qparams, replacement):
    """Update a document created using the local framework
    Parameters
    -----------
    fname: str
        Name of the query should be run
    qparams: dict
        Query parameters. Similar to online query methods
    replacement: dict
        Fields/value pair to be updated. Beware of disallowed fields
        such as time and uid
    """
    try:
        with open(fname, 'r') as fp:
            local_payload = ujson.load(fp)
        qobj = mongoquery.Query(qparams)
        for _sample in local_payload:
            try:
                if qobj.match(_sample):
                    for k, v in replacement.items():
                        _sample[k] = v
            except mongoquery.QueryError:
                pass
        with open(fname, 'w') as fp:
            ujson.dump(local_payload, fp)
    except FileNotFoundError:
        raise RuntimeWarning('Local file {} does not exist'.format(fname))


class LocalSampleReference:
    """Handle sample information locally via json files"""
    def __init__(self, top_dir=conf.local_conn_config['top']):
        self.top_dir = top_dir
        try:
            with open(self._samp_fname, 'r') as fp:
                tmp = ujson.load(fp)
        except (FileNotFoundError, ValueError):
            tmp = []
        try:
            self.sample_list = tmp if tmp else []
        except FileNotFoundError:
            self.sample_list = []

    def create(self, name=None, time=None, uid=None, container=None,
               **kwargs):
        """Create a sample locally

        Parameters
        ----------
        name: str
            Name of the sample
        time: float
            Timestamp generated by the client
        uid: str
            Unique identifier for this sample
        container: str, doct.Document
            The container/group sample is contained within

        Returns
        -------
        payload: dict
            Document dict that was inserted
        """
        # TODO: Allow container to be an object
        if container:
            container = doc_or_uid_to_uid(container)
        payload = dict(uid=uid if uid else str(uuid4()),
                       name=name, time=time if time else ttime.time(),
                       container=container if container else 'NULL',
                       **kwargs)
        self.sample_list.append(payload)
        with open(self._samp_fname, 'w+') as fp:
            ujson.dump(self.sample_list, fp)
        return payload

    @property
    def _samp_fname(self):
        return expanduser(self.top_dir + '/samples.json')

    def update(self, query, replacement):
        _update_local(self._samp_fname, query, replacement)

    def find(self, **kwargs):
        return _find_local(self._samp_fname, kwargs)


class LocalRequestReference:
    """Handle request information locally via json files"""
    def __init__(self, top_dir=conf.local_conn_config['top']):
        """Try to access files. If no file exists, create empty list

        Parameters
        ----------
        top_dir: str
            Directory where local files are stored
        """
        self.top_dir = top_dir
        try:
            with open(self._req_fname, 'r') as fp:
                tmp = ujson.load(fp)
        except FileNotFoundError:
            tmp = []
        try:
            self.request_list = tmp if tmp else []
        except FileNotFoundError:
            self.request_list = []

    @property
    def _req_fname(self):
        return expanduser(self.top_dir + '/requests.json')

    def create(self, sample=None, time=None, uid=None, state='active',
               seq_num=0, **kwargs):
        """Create a request locally

        Parameters
        ----------
        sample: str, doct.Document, optional
            Sample this request points to
        time: float
            Timestamp generated by the client
        uid: str
            Unique identifier for this sample
        state: str
            Defines whether this request is active or not
        seq_num: int
            Shows the order of request in the list of requests

        Returns
        -------
        local_payload: dict
            Request dict that was inserted locally

        """
        if sample:
            sample = doc_or_uid_to_uid(sample)
        payload = dict(uid=uid if uid else str(uuid4()),
                       sample=sample if sample else 'NULL',
                       time=time if time else ttime.time(), state=state,
                       seq_num=seq_num, **kwargs)
        self.request_list.append(payload)
        with open(self._req_fname, 'w+') as fp:
            ujson.dump(self.request_list, fp)
        return payload

    def update(self, query, replacement):
        _update_local(self._req_fname, query, replacement)

    def find(self, **kwargs):
        return _find_local(self._req_fname, kwargs)


class LocalContainerReference:
    """Handle container information locally via json files"""
    def __init__(self, top_dir=conf.local_conn_config['top']):
        self.top_dir = top_dir
        try:
            with open(self._cont_fname, 'r') as fp:
                tmp = ujson.load(fp)
        except FileNotFoundError:
            tmp = []
        self.container_list = tmp if tmp else []

    @property
    def _cont_fname(self):
        return expanduser(self.top_dir + '/containers.json')

    def create(self, uid=None, time=None, container=None, **kwargs):
        """ Create a container locally.

        Parameters
        ----------
        time: float
            Timestamp generated by the client
        uid: str
            Unique identifier for this sample
        container: str, doct.Document, optional
            Container this container is contained within

        Returns
        -------
        payload: dict
            Document dict that was inserted
        """
        if container:
            container = doc_or_uid_to_uid(container)
        payload = dict(uid=uid if uid else str(uuid4()),
                       container=container if container else 'NULL',
                       time=time if time else ttime.time(), **kwargs)
        self.container_list.append(payload)
        with open(self._cont_fname, 'w+') as fp:
            ujson.dump(self.container_list, fp)
        return payload

    def update(self, query, replacement):
        _update_local(self._cont_fname, query, replacement)

    def find(self, **kwargs):
        return _find_local(self._cont_fname, kwargs)