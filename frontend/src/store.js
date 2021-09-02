import { createStore } from 'vuex'
import axios from 'axios'

// API Root : can be set in environmnet, for example:
//  API_ROOT=http://localhost:8000
// If not set, will be empty, which will default to the same host:port as served content.
//const {API_ROOT = 'http://localhost:8000'} = process.env


export default createStore({
    state() {
        return {
            loading: {  // state of loading spinners
                events: false,
                member: false,
            },
            cameraDisplayEnabled: true,  // if false, camera output won't display
            events: {
                active: [], // /api/activeevents
                selected: new Set(JSON.parse(localStorage.getItem('events.selected')) || []), // PKs of selected events
            },
            modal: null,
            member: null, // /api/
        }
    },
    mutations: {
        // Loading States
        SET_LOADING(state, key, isLoading) {
            state.loading[key] = isLoading;
        },
        // Events
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
            // Save to localStorage
            localStorage.setItem('events.selected', JSON.stringify([...state.events.selected])) // as list
        },
        // Member
        SET_MEMBER(state, member) {
            state.member = member
        },
        // Camera State
        SET_CAMERA_DISPLAY(state, render) {
            state.cameraDisplayEnabled = render
        },
        // Modal Screens
        SET_MODAL_NAME(state, name) {
            state.modal = name;  // set to null to clear
        },
    },
    actions: {
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

                    // remove irrelevant selection indexes
                    let eventPks = new Set(events.map(e => e.pk));
                    [...context.state.events.selected]
                        .filter(pk => ! eventPks.has(pk))
                        .forEach(pk => context.commit('TOGGLE_EVENT_PK', pk))
                }
            ).catch(
                (error) => {  // failure
                    context.commit('SET_LOADING', 'events', false)
                    //console.log(error)
                }
            )
        },
        fetchMember(context, memberNum) {
            // memberNum: {type: <contact|member>, number: <int>}
            context.commit('SET_LOADING', 'member', true);
            var uri = null;
            if (memberNum.type === 'contact') {
                uri = '/api/members_cid/' + memberNum.number + '/'
            } else {
                uri = '/api/members_memno/' + memberNum.number + '/'
            }
            axios.get(uri).then(
                (response) => {  // success
                    context.commit('SET_LOADING', 'member', false);
                    context.commit('SET_MEMBER', response.data)
                    context.commit('SET_MODAL_NAME', 'welcome-message')
                }
            ).catch(
                (error) => {  // failure
                    context.commit('SET_LOADING', 'member', false);
                }
            )
            
        },
    }
});