package com.maxima.bbgum;

public interface EventElem {
    void inEvent(EventController v, DatAction action);
    void outEvent(EventController v, DatAction action);
    void timeOutEvent(EventController v, DatAction action);
    boolean isFlowTerm(EventController v);
    int getConclusion(EventController v);
}
