package com.maxima.bbgum;

import java.io.InputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.util.Deque;
import java.util.LinkedList;
import java.util.logging.Level;
import java.util.logging.Logger;

class Session extends Thread {

    private Socket socket;
    private Deque<Frame> writeChunks;
    private Object outGoingMutex;
    private Monitor mon;

    public Session(final String serverAddress, final int port) throws IOException {
        this(new Socket(serverAddress, port));
    }

    public Session(Socket socket) {
        this.socket = socket;
        this.writeChunks = new LinkedList<Frame>();
        this.outGoingMutex = new Object();
        this.mon = new Monitor(this);
    }

    @Override
    public void run() {
        InputStream is = null;
        try {
            is = this.socket.getInputStream();
            for (;;) {
                if (this.readHeadHandler(is) < 0) break;
            }
        } catch (IOException ex) {
            Logger.getLogger(Session.class.getName()).log(Level.SEVERE, null, ex);
        } catch (SessionError ex) {
            Logger.getLogger(Session.class.getName()).log(Level.SEVERE, null, ex);
        } finally {
            try {
                is.close();
            } catch (IOException ex) {
                Logger.getLogger(Session.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }

    public FeedBackData pushBuffer(final byte archetype, final byte[] buffer, final boolean block) {
        return this.mon.pushBuffer(archetype, buffer, block);
    }

    public void deliver(Action action) {

        Frame f = null;

        try {
            f = new Frame(action);
        } catch (FrameError ex) {
            Logger.getLogger(Session.class.getName()).log(Level.SEVERE, null, ex);
            return;
        }

        boolean writeInProgress;

        synchronized (outGoingMutex) {
            writeInProgress = !this.writeChunks.isEmpty();
            this.writeChunks.addLast(f);
        }

        if (!writeInProgress) {
            byte[] data = this.writeChunks.getFirst().getDatFrame();
            OutputStream os;
            try {
                os = this.socket.getOutputStream();
                os.write(data, 0,
                    Frame.FRAME_HEADER_LENGTH +
                    Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH +
                    action.getData().length);
                os.flush();
                this.release();
            } catch (IOException ex) {
                Logger.getLogger(Session.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }

    private void release() throws IOException {

        boolean isNotEmpty;
        synchronized (outGoingMutex) {
            this.writeChunks.pop();
            isNotEmpty = !this.writeChunks.isEmpty();
        }

        if (isNotEmpty) {
            Frame frame = this.writeChunks.getFirst();
            int lengthActionData = frame.getDatAction().getData().length;
            byte[] data = frame.getDatFrame();

            OutputStream os = this.socket.getOutputStream();

            os.write(data, 0,
                Frame.FRAME_HEADER_LENGTH +
                Frame.ACTION_FLOW_INFO_SEGMENT_LENGTH +
                lengthActionData);

            os.flush();
            this.release();
        }
    }

    private int readBodyHandler(InputStream is, int size) throws Exception {
        int rc = 0;

        byte[] receivedBytes = new byte[size];
        int res = is.read(receivedBytes, 0, size);

        if (res < 0) rc = res;
        else {
            Action action = new Action(receivedBytes);
            this.mon.recive(action);
        }

        return rc;
    }

    private int readHeadHandler(InputStream is) throws SessionError {
        int rc = 0;

        byte[] receivedBytes = new byte[Frame.FRAME_HEADER_LENGTH];
        int res = 0;
        try {
            res = is.read(receivedBytes, 0,
                Frame.FRAME_HEADER_LENGTH);
        } catch (IOException ex) {
            String msg = "Problems ocurried when reading"
                    + " frame header from socket";
            Logger.getLogger(Session.class.getName()).log(Level.SEVERE, null, msg);
            throw new SessionError(ex.getMessage());
        }

        if (res < 0) rc = res;
        else {
            int size = 0;
            try {
                size = Frame.decodeDatFrameHeader(receivedBytes);
            } catch (FrameError ex) {
                Logger.getLogger(Session.class.getName()).log(Level.SEVERE, null, ex);
            }

            if (size < 0) rc = size;
            else {
                try {
                    res = this.readBodyHandler(is, size);
                } catch (Exception ex) {
                    String msg = "Problems ocurried when reading"
                        + " frame body from socket";
                    Logger.getLogger(Session.class.getName()).log(Level.SEVERE, null, msg);
                    throw new SessionError(ex.getMessage());
                }
                if (res < 0) rc = res;
            }
        }

        return rc;
    }
}

