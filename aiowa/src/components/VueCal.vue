<template>
    <VueCal
      class="vuecal--blue-theme"
      :events="events"
      :time-from="10 * 60"
      hide-weekends="hide-weekends"
      events-count-on-year-view="events-count-on-year-view"
      :dbl-click-to-navigate="false"
      @event-click="onEventClick"
    >
      <template #cell-content="{ cell, view, goNarrower, events }">
        <span v-if="view.id === 'week'">{{ events.length }}</span>
        <div class="vuecalcell-date" :class="view.id" @click="goNarrower">
          <span class="clickable">{{ cell.content }}</span>
          <span
            class="vuecalcell-events-count"
            v-if="['years', 'year', 'month'].includes(view.id) && events.length"
          >
            {{ customEventsCount(events) }}
          </span>
        </div>
        <span
          class="vuecal__no-event"
          v-if="['week', 'day'].includes(view.id) && !events.length"
        >
          No WFH 👌
        </span>
      </template>
    </VueCal>
  </template>
  
  <script>
  import VueCal from 'vue-cal'; // assuming you have vue-cal installed
  import 'vue-cal/dist/vuecal.css'; // vue-cal's styles
  
  export default {
    components: {
      VueCal,
    },
    props: {
      events: {
        type: Array,
        default: () => [],
      },
      hideWeekends: {
        type: Boolean,
        default: false,
      },
      eventsCountOnYearView: {
        type: Number,
        default: 0,
      },
    },
    data(){
        return {
            selectedEvent: {}, 
            showDialog: false
        }
    },
    methods: { 
        customEventsCount: events => { 
            var AM = 0 
            var PM = 0 
            if (events.length >= 1){ 
            for (i = 0; i < events.length; i++){ 
                if (events[i].class === "AM"){ 
                AM += events[i].count 
                } 
                if (events[i].class === "PM"){ 
                PM += events[i].count 
                } 
            } 
            } 
            return AM + "AM " + PM + "PM" 
        }, 
        onEventClick (event, e) { 
            this.selectedEvent = event 
            this.showDialog = true 
        
            // Prevent navigating to narrower view (default vue-cal behavior). 
            e.stopPropagation() 
        }
    },
  };
  </script>
  
  <style scoped>
  /* Add any component-specific styles here */
  #app { 
  margin: 30px auto; 
  max-width: 580px; 
  height: 350px; 
} 
 
.vuecalevent {background-color: rgba(173, 216, 230, 0.5);} 
.vuecalbody .clickable { 
  color: #4682b4; 
  text-decoration: underline; 
} 
 
.vuecal__cell-date {display: inline-block;}
  </style>
  