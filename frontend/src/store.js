import { createStore } from 'vuex'
import axios from 'axios'
import Cookies from 'js-cookie'

// API Root : can be set in environmnet, for example:
//  API_ROOT=http://localhost:8000
// If not set, will be empty, which will default to the same host:port as served content.
//const {API_ROOT = 'http://localhost:8000'} = process.env

function saveSettings(obj) {
    localStorage.setItem('settings', JSON.stringify(obj))
}

// Settings ranges
const CAMERA_MODES = ['auto', 'front', 'rear']
const AUTOADMIT_TIMES = [null, 1, 2, 3, 5, 10]

const SETTINGS_DEFAULTS = {
    autoAdmitTime: 2,
    cameraMode: 'auto',
    cameraOverlay: true,
    cameraTorch: false,
    listAttendanceFromAll: false,
    sounds: true,
}

export default createStore({
    state() { // $store.state
        // Settings
        const settings = JSON.parse(localStorage.getItem('settings')) || {}
        var key;
        for (key in SETTINGS_DEFAULTS) {
            if (settings[key] === undefined) {
                settings[key] = SETTINGS_DEFAULTS[key]
            }
        }

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
            settings: settings,
            error: {}, // displayed as overlay
        }
    },
    mutations: { // $store.commit()
        // Loading States
        SET_LOADING(state, {key, isLoading}) {
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
        // Settings
        SETTING_TOGGLE(state, name) {
            // toggles settings value as boolean
            state.settings[name] = !state.settings[name]
            saveSettings(state.settings)
        },
        SETTING_CYCLE_CAMERA(state) {
            const i = (CAMERA_MODES.indexOf(state.settings.cameraMode) + 1) % CAMERA_MODES.length
            state.settings.cameraMode = CAMERA_MODES[i]
            saveSettings(state.settings)
        },
        SETTING_CYCLE_AUTOADMIT(state) {
            const i = (AUTOADMIT_TIMES.indexOf(state.settings.autoAdmitTime) + 1) % AUTOADMIT_TIMES.length
            state.settings.autoAdmitTime = AUTOADMIT_TIMES[i]
            saveSettings(state.settings)
        },
        // Error Message
        SET_ERROR(state, {title, message}) {
            console.log(title, message)
            state.error = {
                title: title,
                message: message,
            }
        },
        CLEAR_ERROR(state) {
            state.error = {}
        },
    },
    actions: { // $store.dispatch()
        modalDisplayOpen(context, name) {
            context.commit('SET_MODAL_NAME', name);
            // Stop render of camera while modal dipslay is open
            context.commit('SET_CAMERA_DISPLAY', name ? false : true);
        },
        fetchEvents(context) {
            context.commit('SET_LOADING', {key: 'events', isLoading: true});
            axios.get('/api/activeevents/').then(
                (response) => {  // success
                    context.commit('SET_LOADING', {key: 'events', isLoading: false});
                    let events = response.data;
                    context.commit('SET_EVENTS_ACTIVE', events);
                }
            ).catch(
                (error) => {  // failure
                    context.commit('SET_LOADING', {key: 'events', isLoading: false});
                    context.commit('SET_ERROR', {title: "Error getting active events", message: error})
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
                        // does not display error message
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