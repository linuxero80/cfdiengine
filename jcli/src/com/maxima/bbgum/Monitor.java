package com.maxima.bbgum;

import java.io.IOException;

public final class Monitor {

    static final int TRANSACTION_NUM_START_VALUE = 1;
    static final int TRANSACTION_NUM_LAST_VALUE = 253;
    static final int TRANSACTION_NUM_INCREMENT =  2;
    static final int MAX_NODES = 255;

    private int transNumNext;
    private Session session;
    private Transaction[] poll;
    private EventBlackBox blackBox;

    public Monitor(Session session) {
        this.session = session;
        this.transNumNext = Monitor.TRANSACTION_NUM_START_VALUE;
        this.poll = new Transaction[Monitor.MAX_NODES];

        int iter = 0;
        for (; iter < Monitor.MAX_NODES; iter++) this.poll[iter] = null;

        this.blackBox = new EventBlackBox(this);
    }

    public void reciveActionFromSession(Action action) {

    }

    public void sendToDeliver(Action action) throws IOException {
        this.session.deliver(action);
    }
}
