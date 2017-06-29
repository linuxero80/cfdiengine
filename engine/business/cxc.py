from docmaker.pipeline import DocPipeLine
from misc.tricks import dump_exception
from custom.profile import ProfileReader
from engine.error import ErrorCode
import os


def facturar(logger, pt, req):

    def dm_exec(filename, resdir, usr_id, prefact_id):
        if filename is None:
            return ErrorCode.REQUEST_INCOMPLETE

        dm_builder = 'facxml'
        kwargs = {'usr_id': usr_id, 'prefact_id': prefact_id}
        try:
            dpl = DocPipeLine(logger, resdir,
                rdirs_conf = pt.res.dirs,
                pgsql_conf = pt.dbms.pgsql_conn)
            dpl.run(dm_builder, filename, **kwargs)
            return ErrorCode.SUCCESS
        except:
            logger.error(dump_exception())
            return ErrorCode.DOCMAKER_ERROR

    logger.info("step in {} handler".format(__name__))
    source = ProfileReader.get_content(
                pt.source, ProfileReader.PNODE_UNIQUE)
    resdir = os.path.abspath(os.path.join(
                os.path.dirname(source), os.pardir))
    logger.info(
        'Passing to docmaker as resources directory {}'.format(resdir))
    rc = dm_exec(req.get('filename', None), resdir, req.get('usr_id', None),
                       req.get('prefact_id', None))
    return rc.value
