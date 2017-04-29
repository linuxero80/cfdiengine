import logging
import sys
import os
import psycopg2
from custom.profile import ProfileTree, ProfileReader
from docmaker.error import DocBuilderImptError, DocBuilderStepError, DocBuilderError

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "builders")
    )
)

class DocPipeLine(object):
    """
    creator instance of documents.
    """

    def __init__(self, logger, rdirs_conf = None, pgsql_conf = None):
        self.logger = logger

        if pgsql_conf == None:
            raise DocBuilderError("pgsql config info not fed!!")
        self.pgsql_conf = pgsql_conf

        if rdirs_conf == None:
            raise DocBuilderError("rdirs config info not fed!!")
        self.rdirs_conf = rdirs_conf

    def run(self, b, output_file, **kwargs):
        """runs docmaker's pipeline to create a document"""

        try:
            self.logger.debug("attempting the import of {0} library".format(b))
            doc_mod = __import__(b)

            if not hasattr(doc_mod, "impt_class"):
                msg = "module {0} has no impt_class attribute".format(b)
                raise DocBuilderImptError(msg)

            cname = getattr(doc_mod, "impt_class")

            if not hasattr(doc_mod, cname):
                msg = "module {0} has no {1} class implemented".format(b, cname)
                raise DocBuilderImptError(msg)

            self.builder = getattr(hw_mod, cname)(self.logger)

            if not isinstance(self.builder, BuilderGen) and not issubclass(self.builder.__class__, BuilderGen):
                msg = "unknown support library specification in {0}".format(self.builder)
                raise DocBuilderImptError(msg)

        except (ImportError, DocBuilderImptError) as e:
            self.logger.fatal("{0} support library failure".format(b))
            raise e

        self.__create(
            self.__open_dbms_conn(),
            {p["name"]: p["value"] for p in ProfileReader.get_content(
                self.rdirs_info,
                ProfileReader.PNODE_MANY)
            },
            output_file, **kwargs
        )

    def __create(conn, d_rdirs, output_file, **kwargs):
        """runs pipeline's steps"""
        dat = None

        if len(d_rdirs) > 0:
            pass
        else:
            raise DocBuilderError("slack resource dirs configuration")

        try:
            dat = self.builder.data_acq(conn, d_rdirs, **kwargs)
        except DocBuilderStepError:
            raise
        finally:
            conn.close()

        try:
            self.builder.format_wrt(output_file, dat)
        except DocBuilderStepError:
            raise

        try:
            self.builder.data_rel(dat)
        except DocBuilderStepError:
            raise

    def __open_dbms_conn(self):
        """opens a connection to postgresql"""
        try:
            conn_str = "dbname={0} user={1} host={2} password={3} port={4}".format(
                ProfileReader.get_content(self.pgsql_conf.db, ProfileReader.PNODE_UNIQUE)
                ProfileReader.get_content(self.pgsql_conf.user, ProfileReader.PNODE_UNIQUE)
                ProfileReader.get_content(self.pgsql_conf.host, ProfileReader.PNODE_UNIQUE)
                ProfileReader.get_content(self.pgsql_conf.passwd, ProfileReader.PNODE_UNIQUE)
                ProfileReader.get_content(self.pgsql_conf.port, ProfileReader.PNODE_UNIQUE)
            )

            return psycopg2.connect(conn_str)
        except psycopg2.Error as e:
            self.logger.error(e)
            raise DocBuilderError("dbms was not connected")
        except KeyError as e:
            self.logger.error(e)
            raise DocBuilderError("slack pgsql configuration")
