package com.maxima.bbgum;

import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;
import java.io.ByteArrayInputStream;
import java.io.IOException;

public class BbgumProxy {

    private Session session;

    public BbgumProxy(Session s) {
        this.session = s;
    }

    public ServerReply upLoadBuff(final byte[] buff) throws SessionError, IOException {
        ServerReply rc = new ServerReply();

        ServerReply fo = openBuffTransfer(buff.length);
        int transferId = this.fromBuffToInteger(fo.getReplyBuffer(),"US-ASCII");

        ByteArrayInputStream fin = new ByteArrayInputStream(buff);

        int chunkSizeToUpload = Frame.ACTION_DATA_SEGMENT_MAX_LENGTH - 1;
        long offSet = 0;

        if (buff.length < chunkSizeToUpload) chunkSizeToUpload = (int) buff.length;

        for (;;) {
            if (chunkSizeToUpload == 0) {
                fin.close();
                this.closeBuffTransfer(transferId);
                break;
            } else {
                byte[] dataRead = new byte[chunkSizeToUpload];

                fin.read(dataRead);
                rc.setReplyCode(this.writeBuffTransfer(transferId, dataRead));

                offSet += chunkSizeToUpload;
                long remaining = buff.length - offSet;
                if (remaining < Frame.ACTION_DATA_SEGMENT_MAX_LENGTH - 1) {
                    chunkSizeToUpload = (int)remaining;
                }
            }
        }

        return rc;
    }

    private static String fromBuffToString(final byte[] array ,final String encoding ){
        return new String(
                array, 0, array.length , Charset.forName( encoding ) ).trim();
    }

    private Integer fromBuffToInteger(final byte[] array, final String encoding){
        return Integer.parseInt(new String(
                array, 0, array.length , Charset.forName(encoding)).trim());
    }

    private int writeBuffTransfer(final int transferId, final byte[] data) throws SessionError {
        byte[] ticket = {(byte) transferId};

        if (data.length <= (Frame.ACTION_DATA_SEGMENT_MAX_LENGTH - ticket.length)) {
            byte[] buff = new byte[data.length + ticket.length];
            System.arraycopy(ticket, 0, buff, 0, ticket.length);
            System.arraycopy(data, 0, buff, 1, data.length);
            ServerReply sr = this.session.pushBuffer(Session.EVENT_POST_RAW_BUFFER, buff, true);
            return sr.getReplyCode();
        }

        // We should not have reached at this point :)
        throw new SessionError("Buffer is too big for action data segment");
    }

    private ServerReply openBuffTransfer(final long size) throws SessionError {
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
        throw new SessionError("Buffer is too big for action data segment");
    }

    private int closeBuffTransfer(final int transferId) throws SessionError {
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
