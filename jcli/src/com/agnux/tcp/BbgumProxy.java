package com.agnux.tcp;

import com.maxima.bbgum.*;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;

public class BbgumProxy {

    public static final byte EVENT_POST_RAW_BUFFER = (byte) 0x24;
    public static final byte EVENT_BUFFER_TRANSFER = (byte) 0x28;
    public static final byte EVENT_HELLO = (byte) 0x30;
    private Session session;

    public BbgumProxy(final String serverAddress, final int port) throws BbgumProxyError {
        BasicFactory<Byte, EventController> factory = new BasicFactory<Byte, EventController>();
        factory.subscribe(EVENT_POST_RAW_BUFFER, PostRawBuffer.class);
        factory.subscribe(EVENT_BUFFER_TRANSFER, BufferTransfer.class);
        factory.subscribe(EVENT_HELLO, Hello.class);
        try {
            this.session = new Session(serverAddress, port, factory);
        } catch (IOException ex) {
            throw new BbgumProxyError(
                    "The session with server could not be established: " +
                    ex.toString());
        }
    }

    public int sayHello() throws BbgumProxyError {
        ServerReply rc = null;
        try {
            byte[] data = "HELLO".getBytes("US-ASCII");
            rc = this.session.pushBuffer(EVENT_HELLO, data, true);
        } catch (Exception ex) {
            throw new BbgumProxyError(
                    "Unexpected protocol session error when saying hello: " +
                    ex.toString());
        }
        return rc.getReplyCode();
    }

    public ServerReply uploadBuff(final byte[] buff) throws BbgumProxyError {
        try {
            // Run state machine to transfer the buffer
            return this.runSmBuffTransfer(buff);
        } catch (SessionError ex) {
            throw new BbgumProxyError(
                    "Unexpected protocol session error during upload: " +
                    ex.toString());
        } catch (IOException ex) {
            throw new BbgumProxyError(
                    "Unexpected IO error during upload: " +
                    ex.toString());
        }
    }

    private ServerReply runSmBuffTransfer(final byte[] buff) throws SessionError, IOException {
        ServerReply replyObt = openBuffTransfer(buff.length);

        if ( replyObt.getReplyCode() != 0 ) {
            throw new SessionError("It was not possible to open a buffer transfer");
        }

        int sid = this.fromBuffToInteger(replyObt.getReplyBuffer(), "US-ASCII");
        ByteArrayInputStream fin = new ByteArrayInputStream(buff);

        int chunkSize = Frame.ACTION_DATA_SEGMENT_MAX_LENGTH - 1;
        long offSet = 0;

        if (buff.length < chunkSize) chunkSize = buff.length;

        for (;;) {
            if (chunkSize == 0) {
                fin.close();
                return this.closeBuffTransfer(sid);
            }

            byte[] pivotBuff = new byte[chunkSize];
            fin.read(pivotBuff);
            int resolution = this.writeBuffTransfer(sid, pivotBuff);
            if ( resolution != 0) {
                fin.close();
                this.closeBuffTransfer(sid);
                throw new SessionError("Server side experimenting issues when writing");
            }

            offSet += chunkSize;
            long remaining = buff.length - offSet;
            if (remaining < Frame.ACTION_DATA_SEGMENT_MAX_LENGTH - 1) chunkSize = (int)remaining;
        }
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
            ServerReply sr = this.session.pushBuffer(EVENT_POST_RAW_BUFFER, buff, true);
            return sr.getReplyCode();
        }

        // We should not have reached at this point :)
        throw new SessionError("Buffer is too big for action data segment");
    }

    private ServerReply openBuffTransfer(final long size) throws SessionError {
        // Internal command to start
        // server side's transfer manager (Post Mode)
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
            return this.session.pushBuffer(EVENT_BUFFER_TRANSFER, buff, true);
        }

        // We should not have reached at this point :)
        throw new SessionError("Buffer is too big for action data segment");
    }

    private ServerReply closeBuffTransfer(final int transferId) throws SessionError {
        // Internal command for server side's transfer manager
        byte closeCmdId = (byte) 0xCC;

        byte[] id = {(byte) transferId};
        byte[] cmd = {closeCmdId};
        byte[] buff;

        buff = new byte[id.length + cmd.length];
        System.arraycopy(cmd, 0, buff, 0, cmd.length);
        System.arraycopy(id, 0, buff, 1, id.length);
        return this.session.pushBuffer(EVENT_BUFFER_TRANSFER, buff , true);
    }
}
