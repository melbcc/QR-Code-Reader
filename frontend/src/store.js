import { createStore } from 'vuex'
import axios from 'axios'

// API Root : can be set in environmnet, for example:
//  API_ROOT=http://localhost:8000
// If not set, will be empty, which will default to the same host:port as served content.
//const {API_ROOT = 'http://localhost:8000'} = process.env


export default createStore({
    state() {
        return {
            loading: {
                events: false,
            },
            cameraDisplayEnabled: true,  // if false, camera output won't display
            events: {
                active: [],
                selected: new Set(JSON.parse(localStorage.getItem('events.selected')) || []), // PKs of selected events
            },
        }
    },
    mutations: {
        // Events
        SET_LOADING_EVENTS(state, loading) {
            state.loading.events = loading;
        },
        SET_EVENTS_ACTIVE(state, events) {
            state.events.active = events;
            // TODO: prune selected
        },
        TOGGLE_EVENT_PK(state, pk) {
            if (state.events.selected.has(pk)) {
                state.events.selected.delete(pk)
            } else {
                state.events.selected.add(pk)
            }
            // Store in local storage
            localStorage.setItem('events.selected', JSON.stringify([...state.events.selected])) // as list
        },
        // Camera State
        SET_CAMERA_DISPLAY(state, render) {
            state.cameraDisplayEnabled = render;
        },
    },
    actions: {
        modalDisplayOpen(context, isOpen) {
            // Stop render of camera while modal dipslay is open
            context.commit('SET_CAMERA_DISPLAY', isOpen ? false : true);
        },
        fetchEvents(context) {
            context.commit('SET_LOADING_EVENTS', true);
            axios.get('/api/activeevents/').then(response => {
                context.commit('SET_LOADING_EVENTS', false);
                let events = response.data;
                context.commit('SET_EVENTS_ACTIVE', events);

                // remove irrelevant selection indexes
                let eventPks = new Set(events.map(e => e.pk));
                [...context.state.events.selected]
                    .filter(pk => ! eventPks.has(pk))
                    .forEach(pk => context.commit('TOGGLE_EVENT_PK', pk))
            })
        },
    }
});