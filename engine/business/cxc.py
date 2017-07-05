from docmaker.pipeline import DocPipeLine
from pac.connector import setup_pac
from misc.tricks import dump_exception
from custom.profile import ProfileReader
from misc.helperstr import HelperStr
from engine.error import ErrorCode
import tempfile
import os


def facturar(logger, pt, req):

    def dm_exec(filename, resdir, usr_id, prefact_id):
        dm_builder = 'facxml'
        kwargs = {'usr_id': usr_id, 'prefact_id': prefact_id}
        try:
            dpl = DocPipeLine(logger, resdir,
                rdirs_conf=pt.res.dirs,
                pgsql_conf=pt.dbms.pgsql_conn)
            dpl.run(dm_builder, filename, **kwargs)
            return ErrorCode.SUCCESS
        except:
            logger.error(dump_exception())
            return ErrorCode.DOCMAKER_ERROR

    def pac_sign(f, resdir):
        try:
            # Here it would be placed, code calling
            # the pac connector mechanism
            logger.debug('Getting a pac connector as per config profile')
            pac, err = setup_pac(logger, pt.tparty.pac)
            if pac is None:
                raise Exception(err)
            logger.debug('File to sign {}'.format(f))
            with open(f) as t:
                signed = pac.stamp(t.read(), 'HARD_XID')
                logger.debug(signed)
            return ErrorCode.SUCCESS, f
        except:
            logger.error(dump_exception())
            return ErrorCode.THIRD_PARTY_ISSUES

    def store(f):
        try:
            # Here it would be placed, code for
            # saving relevant info of newer cfdi in dbms
            logger.debug('saving relevant info of {} in dbms', f)
            return ErrorCode.SUCCESS
        except:
            logger.error(dump_exception())
            return ErrorCode.ETL_ISSUES

    logger.info("stepping in factura handler within {}".format(__name__))

    source = ProfileReader.get_content(pt.source, ProfileReader.PNODE_UNIQUE)
    resdir = os.path.abspath(os.path.join(os.path.dirname(source), os.pardir))
    usr_id = req.get('usr_id', None)
    prefact_id = req.get('prefact_id', None)

    logger.debug('Using as resources directory {}'.format(resdir))

    tmp_dir = tempfile.gettempdir()
    filename = os.path.join(tmp_dir, HelperStr.random_str())
    rc = dm_exec(filename, resdir, usr_id, prefact_id)

    if rc == ErrorCode.SUCCESS:
        rc, outfile = pac_sign(filename, resdir)
        if rc == ErrorCode.SUCCESS:
            rc = store(outfile)

    return rc.value
