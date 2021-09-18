import { createStore } from 'vuex'
import axios from 'axios'
import Cookies from 'js-cookie'

// API Root : can be set in environmnet, for example:
//  API_ROOT=http://localhost:8000
// If not set, will be empty, which will default to the same host:port as served content.
//const {API_ROOT = 'http://localhost:8000'} = process.env


export default createStore({
    state() { // $store.state
        return {
            loading: {  // state of loading spinners
                events: false,
                member: false,
                attendees: false,
            },
            cameraDisplayEnabled: true,  // if false, camera output won't display
            events: {
                active: [], // /api/activeevents
                selected: new Set(JSON.parse(localStorage.getItem('events.selected')) || []), // PKs of selected events
            },
            modal: null,
            // Settings
            settings: JSON.parse(localStorage.getItem('settings')) || {
                listAttendanceFromAll: false,
                // TODO: populate from burger menu
            },
        }
    },
    mutations: { // $store.commit()
        // Loading States
        SET_LOADING(state, key, isLoading) {
            state.loading[key] = isLoading;
        },
        // Events
        SET_EVENTS_ACTIVE(state, events) {
            state.events.active = events;

            // remove irrelevant selection indexes
            let eventPks = new Set(events.map(e => e.pk));
            [...state.events.selected]
                .filter(pk => ! eventPks.has(pk))
                .forEach(pk => state.events.selected.delete(pk))

            // Save to localStorage
            localStorage.setItem('events.selected', JSON.stringify([...state.events.selected])) // as list
        },
        TOGGLE_EVENT_PK(state, pk) {
            if (state.events.selected.has(pk)) {
                state.events.selected.delete(pk)
            } else {
                state.events.selected.add(pk)
            }
            // Save to localStorage
            localStorage.setItem('events.selected', JSON.stringify([...state.events.selected])) // as list
        },
        // Camera State
        SET_CAMERA_DISPLAY(state, render) {
            state.cameraDisplayEnabled = render
        },
        // Modal Screens
        SET_MODAL_NAME(state, name) {
            state.modal = name  // set to null to clear
        },
    },
    actions: { // $store.dispatch()
        modalDisplayOpen(context, name) {
            context.commit('SET_MODAL_NAME', name);
            // Stop render of camera while modal dipslay is open
            context.commit('SET_CAMERA_DISPLAY', name ? false : true);
        },
        fetchEvents(context) {
            context.commit('SET_LOADING', 'events', true);
            axios.get('/api/activeevents/').then(
                (response) => {  // success
                    context.commit('SET_LOADING', 'events', false);
                    let events = response.data;
                    context.commit('SET_EVENTS_ACTIVE', events);
                }
            ).catch(
                (error) => {  // failure
                    context.commit('SET_LOADING', 'events', false)
                    // TODO: set error message
                }
            )
        },
        submitAttendance(context, member) {
            //! TODO: submi attendance via api call
            context.commit('POP_MEMBER')
            if (! context.state.memberStack) {
                context.commit('SET_MODAL_NAME', null)
            }
        },
    },
    getters: {
        csrftoken(state) {
            // get if not already defined
            let csrftoken = Cookies.get('csrftoken')
            if (!csrftoken) { // probably only necessary for dev
                console.log('get token')
                axios.get('/token/csrf').then(
                    (response) => { // success
                        Cookies.set('csrftoken', response.data.token)
                    }
                ).catch(
                    (error) => { // failure
                        console.log('ERROR while getting csrftoken:', error)
                        // TODO: display error
                    }
                )
                //! FIXME: promise is not complete, first call always yields nothing.
                //!        workaround: called when app is first created.
            }
            return csrftoken
        },
        selectedEvents(state) {
            return state.events.active.filter(event => state.events.selected.has(event.pk))
        },
    },
});