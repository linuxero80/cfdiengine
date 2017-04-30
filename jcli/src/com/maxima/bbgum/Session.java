package com.maxima.bbgum;

import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.util.Deque;
import java.util.LinkedList;

class ProtocolSession {

    private Socket socket;
    private Deque<DatFrame> writeChunks;
    private Object outGoingMutex;

    public ProtocolSession(Socket socket) {
        this.socket = socket;
        this.writeChunks = new LinkedList<>();
        this.outGoingMutex = new Object();
    }

    private void release() throws IOException {

        boolean isNotEmpty;
        synchronized (outGoingMutex) {
            this.writeChunks.pop();
            isNotEmpty = !this.writeChunks.isEmpty();
        }

        if (isNotEmpty) {
            DatFrame frame = this.writeChunks.getFirst();
            int lengthActionData = frame.getDatAction().getData().length;
            byte[] data = frame.getDatFrame();

            OutputStream os = this.socket.getOutputStream();

            os.write(data, 0,
                DatFrame.DAT_FRAME_HEADER_LENGTH +
                DatFrame.DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH +
                lengthActionData);

            os.flush();

            this.release();
        }
    }
}

