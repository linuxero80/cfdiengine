package com.maxima.bbgum;

import java.io.IOException;

final class Monitor {

    static final int TRANSACTION_NUM_START_VALUE = 1;
    static final int TRANSACTION_NUM_LAST_VALUE = 253;
    static final int TRANSACTION_NUM_INCREMENT =  2;
    static final int MAX_NODES = 255;

    private int nextNum;
    private Session session;
    private Transaction[] poll;
    private EventBlackBox blackBox;

    public Monitor(Session session) {
        this.session = session;
        this.nextNum = Monitor.TRANSACTION_NUM_START_VALUE;
        this.poll = new Transaction[Monitor.MAX_NODES];

        int iter = 0;
        for (; iter < Monitor.MAX_NODES; iter++) this.poll[iter] = null;

        this.blackBox = new EventBlackBox(this);
    }

    private synchronized int requestNextNum() throws Exception {
        int index = this.nextNum;

        if ((this.poll[index] != null) &&
            (index == Monitor.TRANSACTION_NUM_LAST_VALUE )) {

            // From the first shelf we shall start
            // the quest of an available one if
            // next one was ocuppied and the last one.

            index = Monitor.TRANSACTION_NUM_START_VALUE;
        }

        if (this.poll[index] == null) {

            // When the shelf is available we shall return it
            // before we shall set nextNum variable up for
            // later calls to current function.

            if (index == Monitor.TRANSACTION_NUM_LAST_VALUE) {
                this.nextNum = Monitor.TRANSACTION_NUM_START_VALUE;
            } else {
                this.nextNum = index + Monitor.TRANSACTION_NUM_INCREMENT;
            }
            return index;
        }

        {
            // If you've reached this code block my brother, so...
            // you migth be in trouble soon. By the way you seem
            // a lucky folk and perhaps you would find a free
            // shelf by performing sequential search with awful
            // linear time. Otherwise the matter is fucked :(

            int i = 0;

            do {
                index += Monitor.TRANSACTION_NUM_INCREMENT;
                i++;
            } while ((this.poll[index] != null) && (i < Monitor.MAX_NODES));

            if (i == (Monitor.MAX_NODES - 1)) {
                String msg = "Poll of transactions to its maximum capacity";
                throw new Exception(msg);
            }
            this.nextNum = index + Monitor.TRANSACTION_NUM_INCREMENT;
            return index;
        }
    }

    private boolean isServerTransaction(final int num) {
        return ((num % 2) == 0);
    }

    private synchronized Transaction getTransactionFromPoll(int index) {
        return (this.poll[index] != null) ? this.poll[index] : null;
    }

    private synchronized void destroyTransactionInPoll(int index) {
        this.poll[index] = null;
    }

    public void recive(Action action) {
        // Receives an action from upper layer

    }

    public void send(Action action) {
        // Sends action to upper layer
        this.session.deliver(action);
    }

    public FeedBackData pushBuffer(final byte archetype, final byte[] buffer, final boolean block) {
        FeedBackData rd = null;
        return rd;
    }
}
