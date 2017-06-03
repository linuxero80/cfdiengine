package com.maxima.bbgum;

import java.io.UnsupportedEncodingException;

public class JCliConnector {

    private Session session;

    public JCliConnector(Session s) {
        this.session = s;
    }

    public ServerReply openPostBufferTransfer(long size) throws SessionError {
        // Internal command for server side's transfer manager
        byte openPostCmdId = (byte) 0xBB;

        byte[] cmd = {openPostCmdId};
        byte[] ascii;
        String args = String.valueOf(size);
        try {
            ascii = args.getBytes("US-ASCII");
        } catch (UnsupportedEncodingException ex) {
            throw new SessionError(ex.toString());
        }

        if ((Frame.ACTION_DATA_SEGMENT_MAX_LENGTH) >= (cmd.length + ascii.length)) {
            byte[] buff = new byte[(cmd.length + ascii.length)];
            System.arraycopy(cmd, 0, buff, 0, cmd.length);
            System.arraycopy(ascii, 0, buff, 1, ascii.length);
            return this.session.pushBuffer(Session.EVENT_BUFFER_TRANSFER, buff, true);
        }

        // We should not have reached at this point :)
        throw new SessionError("Buffer is too big");
    }

    private int closeBufferTransfer(int transferId) throws SessionError {
        // Internal command for server side's transfer manager
        byte closeCmdId = (byte) 0xCC;

        byte[] id = {(byte) transferId};
        byte[] cmd = {closeCmdId};
        byte[] buff;

        buff = new byte[id.length + cmd.length];
        System.arraycopy(cmd, 0, buff, 0, cmd.length);
        System.arraycopy(id, 0, buff, 1, id.length);
        ServerReply sr = this.session.pushBuffer(Session.EVENT_BUFFER_TRANSFER, buff , true);
        return sr.getReplyCode();
    }
}
