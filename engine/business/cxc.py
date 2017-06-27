from docmaker.pipeline import DocPipeLine
from misc.tricks import dump_exception
from engine.error import ErrorCode


def facturar(logger, pt, req):

    def dm_exec(usr_id, prefact_id):
        dm_builder = 'facxml'
        kwargs = {'usr_id': usr_id, 'prefact_id': prefact_id}
        try:
            dpl = DocPipeLine(logger, resdir,
                rdirs_conf = pt.res.dirs,
                pgsql_conf = pt.dbms.pgsql_conn)
            dpl.run(dm_builder, args.dm_output, **kwargs)
            return ErrorCode.SUCCESS
        except:
            logger.error(dump_exception())
            return ErrorCode.DOCMAKER_ERROR

    rc = dm_exec(req.get('usr_id', None), req.get('prefact_id', None))
    return rc.value
