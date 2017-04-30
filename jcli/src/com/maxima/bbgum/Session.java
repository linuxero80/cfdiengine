package com.maxima.bbgum;

import java.io.InputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.util.Deque;
import java.util.LinkedList;


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

    public void run() {
        try {
            InputStream is = this.socket.getInputStream();
            for (;;) {
                if (this.readHeadHandler(is) < 0) break;
            }
            is.close();
        } catch (IOException e) {
            // we should capture e info upon logger
        }
    }

    public void deliver(Action action) throws IOException {

        Frame frame = new Frame(action);
        boolean writeInProgress;

        synchronized (outGoingMutex) {
            writeInProgress = !this.writeChunks.isEmpty();
            this.writeChunks.addLast(frame);
        }

        if (!writeInProgress) {

            byte[] data = this.writeChunks.getFirst().getDatFrame();
            OutputStream os = this.socket.getOutputStream();

            os.write(data, 0,
                Frame.DAT_FRAME_HEADER_LENGTH +
                Frame.DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH +
                action.getData().length);

            os.flush();
            this.release();
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
                Frame.DAT_FRAME_HEADER_LENGTH +
                Frame.DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH +
                lengthActionData);

            os.flush();
            this.release();
        }
    }

    private int readBodyHandler(InputStream is, int size) throws IOException {
        int rc = 0;

        byte[] receivedBytes = new byte[size];
        int res = is.read(receivedBytes, 0, size);

        if (res < 0) rc = res;
        else {
            Action action = new Action(receivedBytes);
            this.mon.reciveActionFromSession(action);
        }

        return rc;
    }

    private int readHeadHandler(InputStream is) throws IOException {
        int rc = 0;

        byte[] receivedBytes = new byte[Frame.DAT_FRAME_HEADER_LENGTH];
        int res = is.read(receivedBytes, 0,
                Frame.DAT_FRAME_HEADER_LENGTH);

        if (res < 0) rc = res;
        else {
            int size = Frame.decodeDatFrameHeader(receivedBytes);

            if (size < 0) rc = size;
            else {
                res = this.readBodyHandler(is, size);
                if (res < 0) rc = res;
            }
        }

        return rc;
    }
}

