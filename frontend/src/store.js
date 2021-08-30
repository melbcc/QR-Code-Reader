import { createStore } from 'vuex'

export default createStore({
    state() {
        return {
            loading: {
                events: false,
            },
            cameraDisplayEnabled: true,  // if false, camera output won't display
        }
    },
    mutations: {
        SET_LOADING_EVENTS(state, loading) {
            state.loading.events = loading;
        },
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
            
        },
        
    }
});