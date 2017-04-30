package com.maxima.bbgum;

public interface EventElem {
    void inComming(EventController v, Action action);
    void outComming(EventController v, Action action);
    void timeOut(EventController v, Action action);
    boolean isFlowTerm(EventController v);
    int getConclusion(EventController v);
}
