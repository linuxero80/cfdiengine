from abc import ABCMeta, abstractmethod
import psycopg2

class BuilderGen(metaclass=ABCMeta):
    """
    Builder interface base class.
    """

    def  __init__(self, logger):
        self.logger = logger

    def __str__(self):
        return self.__class__.__name__

    def pg_query(self, conn, sql):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            if len(rows) > 0:
                return rows
            else:
                raise DocBuilderStepError('There is not data retrieved')
        except psycopg2.Error as e:
            raise DocBuilderStepError("an error occurred when executing query")

    @abstractmethod
    def data_acq(self, conn, d_rdirs, **kwargs):
        """document's data acquisition"""

    @abstractmethod
    def format_wrt(self, output_file, dat):
        """writes the document"""

    @abstractmethod
    def data_rel(self, dat):
        """release resources previously gotten"""
