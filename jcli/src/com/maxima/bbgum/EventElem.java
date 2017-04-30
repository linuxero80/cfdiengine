package com.maxima.bbgum;

public interface EventElem {
    void inComming(EventController v, DatAction action);
    void outComming(EventController v, DatAction action);
    void timeOut(EventController v, DatAction action);
    boolean isFlowTerm(EventController v);
    int getConclusion(EventController v);
}
