from custom.profile import ProfileReader
import psycopg2
import psycopg2.extras


class HelperPg(object):
    """
    """

    @staticmethod
    def connect(conf):
        """opens a connection to postgresql"""
        conn_str = "dbname={0} user={1} host={2} password={3} port={4}".format(
            ProfileReader.get_content(conf.db, ProfileReader.PNODE_UNIQUE),
            ProfileReader.get_content(conf.user, ProfileReader.PNODE_UNIQUE),
            ProfileReader.get_content(conf.host, ProfileReader.PNODE_UNIQUE),
            ProfileReader.get_content(conf.passwd, ProfileReader.PNODE_UNIQUE),
            ProfileReader.get_content(conf.port, ProfileReader.PNODE_UNIQUE)
        )
        return psycopg2.connect(conn_str)

    @staticmethod
    def query(conn, sql):
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) > 0:
            return rows

        # We should not have reached this point
        raise Exception('There is not data retrieved')
