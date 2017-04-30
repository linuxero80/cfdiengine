package com.maxima.bbgum;

import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;

public final class DatFrame {

    private byte[] header;
    private byte[] body;
    int actionLength;

    public static final int DAT_FRAME_HEADER_LENGTH = 4;
    public static final int DAT_FRAME_BODY_MAX_LENGTH = 512;
    public static final int DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH = 2;
    public static final int DAT_ACTION_ACK_DATA_SIZE = 2;
    public static final int DAT_FRAME_FULL_MAX_LENGTH = DAT_FRAME_HEADER_LENGTH + DAT_FRAME_BODY_MAX_LENGTH;
    public static final int DAT_ACTION_DATA_SEGMENT_MAX_LENGTH = DAT_FRAME_BODY_MAX_LENGTH - DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH;
    public static final int C_NULL_CHARACTER = 0;

    public static final byte DAT_ACK = (byte) 0x06;
    public static final byte DAT_NAK = (byte) 0x15;

    public DatFrame(DatAction action) {
        this();
        this.actionLength = DatFrame.DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH
            + action.getData().length;
        this.header = DatFrame.encodeDatFrameHeader(actionLength);
        this.body[0] = action.getId();
        this.body[1] = action.getTransaction();
        System.arraycopy(action.getData(), 0, this.body,
            DatFrame.DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH,
            action.getData().length);
    }

    private DatFrame() {
        this.header = new byte[DatFrame.DAT_FRAME_HEADER_LENGTH];
        this.body = new byte[DatFrame.DAT_FRAME_BODY_MAX_LENGTH];
        this.actionLength = 0;
    }

    public byte[] getDatFrame() {
        byte[] data = new byte[DatFrame.DAT_FRAME_FULL_MAX_LENGTH];
        System.arraycopy(this.header, 0, data, 0, this.header.length);
        System.arraycopy(this.body, 0, data, this.header.length, this.body.length);
        return data;
    }

    public final DatAction getDatAction() {
        DatAction action = new DatAction();
        int dataBufferSize = this.actionLength
            - DatFrame.DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH;
        byte[] data = new byte[dataBufferSize];

        System.arraycopy(this.body,
            DatFrame.DAT_ACTION_FLOW_INFO_SEGMENT_LENGTH, data, 0,
            data.length);

        action.setId(this.body[0]);
        action.setTransaction(this.body[1]);
        action.setData(data);

        return action;
    }

    public static byte[] encodeDatFrameHeader(final int actionLength) {
        byte[] header = new byte[DatFrame.DAT_FRAME_HEADER_LENGTH];
        byte[] ascii;

        try {
            String result = String.format("%4d", actionLength);
            ascii = result.getBytes("US-ASCII");

            for (int index = 0; index < ascii.length; ++index) header[index] = ascii[index];

        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }

        return header;
    }

    public static int decodeDatFrameHeader(final byte header[]) {
        int rc = 0;

        if (header.length == DatFrame.DAT_FRAME_HEADER_LENGTH) {
            Charset charset = Charset.forName("US-ASCII");
            String strHeader = new String(header, 0, header.length, charset);
            rc = Integer.parseInt(strHeader.trim());

            if (rc > DatFrame.DAT_FRAME_BODY_MAX_LENGTH) {
                // we should throw an exception here
                return rc = -1201;
            }
        } else {
            rc = -1200; // we should throw an exception here
        }

        return rc;
    }
}
