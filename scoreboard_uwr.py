#!/usr/bin/python3.5
"""
/* scoreboard
 * Copyright (C) Creative Commons Alike V4.0
 * pascaldagornet@yahoo.de
 * No warranty
 */
"""
import gi
#
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, Gdk as gdk, GLib, GObject as gobject

gobject.threads_init()
import string  # not used for now
import os  # not used for now
from datetime import datetime, timedelta
import time
import threading


############################################################################################
# threading the counting of all timers of the game when the start/stop button is clicked
# in order not to block the programm
#
class _IdleObject(gobject.GObject):
    """
    Override gobject.GObject to always emit signals in the main thread
    by emitting on an idle handler
    """

    def __init__(self):
        gobject.GObject.__init__(self)

    #

    def emit(self, *args):
        gobject.idle_add(gobject.GObject.emit, self, *args)


#
class _time_controlThread(threading.Thread, _IdleObject):

    '''thread which uses gobject signals to return information to the GUI.'''
    #
    __gsignals__ = {"update_timers": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])}

    def __init__(self):
        threading.Thread.__init__(self)
        _IdleObject.__init__(self)
        self.cancelled = False
        #

    def run(self):

        global start_time_of_the_game
        global buffer_last_started_ellapsed_period_time_seconds
        global buffer_last_time_start
        global buffer_last_time_start_penalty
        global buffer_last_time_start_timeout
        global buffer_last_time_start_break
        global buffer_last_started_ellapsed_period_time
        global buffer_last_time_stop
        global running_penalty
        global running_break
        global counter_seconds_board
        global ellapsed_period_time_seconds
        global ellapsed_time_game_in_seconds
        global period_time_in_second
        global game_started
        global game_not_cancelled
        global action_start_time_of_the_game_is_ACTIVE
        global running_penalty
        global running_timeout
        global running_break
        global running_time_penalty_player_1_left
        global running_time_penalty_player_2_left
        global running_time_penalty_player_3_left
        global running_time_penalty_player_1_right
        global running_time_penalty_player_2_right
        global running_time_penalty_player_3_right
        global time_penalty_player_1_left_initialized
        global time_penalty_player_2_left_initialized
        global time_penalty_player_3_left_initialized
        global time_penalty_player_1_right_initialized
        global time_penalty_player_2_right_initialized
        global time_penalty_player_3_right_initialized
        global counter_seconds_special_time_sequence
        global ellapsed_special_time_sequence_seconds
        global ellapsed_maximum_time_special_sequence_seconds
        global buffer_time_start_special_time_sequence
        global stopped_special_time_sequence
        global timepenalty_maximum_seconds
        global ellapsed_time_penalty_player_1_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_1_left_seconds
        global counter_seconds_time_penalty_player_1_left
        global buffer_last_time_stop_of_the_timepenalty_player1_left
        global buffer_last_time_start_of_the_timepenalty_player1_left
        global ellapsed_time_penalty_player_2_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_2_left_seconds
        global counter_seconds_time_penalty_player_2_left
        global buffer_last_time_stop_of_the_timepenalty_player2_left
        global buffer_last_time_start_of_the_timepenalty_player2_left
        global ellapsed_time_penalty_player_3_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_3_left_seconds
        global counter_seconds_time_penalty_player_3_left
        global buffer_last_time_stop_of_the_timepenalty_player3_left
        global buffer_last_time_start_of_the_timepenalty_player3_left
        #
        global ellapsed_time_penalty_player_1_right_seconds
        global buffer_last_started_ellapsed_time_penalty_player_1_right_seconds
        global counter_seconds_time_penalty_player_1_right
        global buffer_last_time_stop_of_the_timepenalty_player1_right
        global buffer_last_time_start_of_the_timepenalty_player1_right
        global ellapsed_time_penalty_player_2_right_seconds
        global buffer_last_started_ellapsed_time_penalty_player_2_right_seconds
        global counter_seconds_time_penalty_player_2_right
        global buffer_last_time_stop_of_the_timepenalty_player2_right
        global buffer_last_time_start_of_the_timepenalty_player2_right
        global ellapsed_time_penalty_player_3_right_seconds
        global buffer_last_started_ellapsed_time_penalty_player_3_right_seconds
        global counter_seconds_time_penalty_player_3_right
        global buffer_last_time_stop_of_the_timepenalty_player3_right
        global buffer_last_time_start_of_the_timepenalty_player3_right
        global watch_stop
        global now_dont_stop


        ''' all 8 timer update calculation logic will be here
        NO update of labels here
        NO interaction with the GUI
        ONLY time calculation of counters or decision parameters for appearance in all labels'''

        #
        game_not_cancelled = True
        # that parameter set to False in the GUI during exit will allow the threading to
        # end properly without an error or hanging

        #print("def run: first run; game_started", game_started)

        while game_not_cancelled:

            if game_started:

                if watch_stop: # standard logic with start / stop of the countdown

                    if action_start_time_of_the_game_is_ACTIVE and counter_seconds_board > 0:
                        #
                        # game running (not stopped) and time not already down to zero.
                        # this is typically a running period of a game after a game was started
                        # it calculates here the board period time = countdown
                        # the timeout or break or penalty countdown are not calculated here because they
                        # dont run when the game is running
                        #
                        #print("def run: countdown running")
                        difference_date_time = datetime.now() - buffer_last_time_start
                        #print("def run: difference_date_time ", difference_date_time)
                        difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                      int(difference_date_time.seconds)
                        #print("def run: difference_date_time_in_seconds between buffer_last_time_start and now  ",
                        #        difference_date_time_in_seconds)

                        if difference_date_time_in_seconds >= 0:
                            ellapsed_period_time_seconds = buffer_last_started_ellapsed_period_time_seconds + \
                                                           difference_date_time_in_seconds
                            counter_seconds_board = period_time_in_second - ellapsed_period_time_seconds
                        else:
                        #    print("def run: difference_date_time_in_seconds identified negativ; set to zero  ")
                        #    difference_date_time_in_seconds = 0
                            counter_seconds_board = 0

                        # perhaps stop here all timepenalty
                        #print("def run: counter_seconds_board ", counter_seconds_board)

                        #
                        # calculate board of all six timepenalty players = countdown
                        #
                        # *************   LEFT   ***************
                        if running_time_penalty_player_1_left and \
                                counter_seconds_time_penalty_player_1_left == timepenalty_maximum_seconds and \
                                not time_penalty_player_1_left_initialized:
                            buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = 0
                            buffer_last_time_start_of_the_timepenalty_player1_left = datetime.now()
                        #    print("FIRST countdown time_penalty_player_1_left")
                        #    print("buffer start time_penalty_player_1_left initialized")
                            time_penalty_player_1_left_initialized = True
                        #
                        if running_time_penalty_player_1_left:
                            difference_date_time = datetime.now() - \
                                                   buffer_last_time_start_of_the_timepenalty_player1_left
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                            ellapsed_time_penalty_player_1_left_seconds = buffer_last_started_ellapsed_time_penalty_player_1_left_seconds + \
                                difference_date_time_in_seconds
                            counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds - \
                                                                         ellapsed_time_penalty_player_1_left_seconds
                        #    print("countdown time_penalty_player_1_left")
                        #
                        if running_time_penalty_player_2_left and \
                                counter_seconds_time_penalty_player_2_left == timepenalty_maximum_seconds and \
                                not time_penalty_player_2_left_initialized:
                            buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = 0
                            buffer_last_time_start_of_the_timepenalty_player2_left = datetime.now()
                        #    print("FIRST countdown time_penalty_player_2_left")
                        #    print("buffer start time_penalty_player_2_left initialized")
                            time_penalty_player_2_left_initialized = True
                        #
                        if running_time_penalty_player_2_left:
                            difference_date_time = \
                                datetime.now() - buffer_last_time_start_of_the_timepenalty_player2_left
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                            ellapsed_time_penalty_player_2_left_seconds = \
                                buffer_last_started_ellapsed_time_penalty_player_2_left_seconds + \
                                difference_date_time_in_seconds
                            counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds - \
                                                                         ellapsed_time_penalty_player_2_left_seconds
                        #    print("countdown time_penalty_player_2_left")
                            #
                        if running_time_penalty_player_3_left and \
                                counter_seconds_time_penalty_player_3_left == timepenalty_maximum_seconds and \
                                not time_penalty_player_3_left_initialized:
                            buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = 0
                            buffer_last_time_start_of_the_timepenalty_player3_left = datetime.now()
                        #    print("FIRST countdown time_penalty_player_3_left")
                        #    print("buffer start time_penalty_player_3_left initialized")
                            time_penalty_player_3_left_initialized = True
                            #
                        if running_time_penalty_player_3_left:
                            difference_date_time = datetime.now() - \
                                                   buffer_last_time_start_of_the_timepenalty_player3_left
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                            ellapsed_time_penalty_player_3_left_seconds = \
                                buffer_last_started_ellapsed_time_penalty_player_3_left_seconds + \
                                difference_date_time_in_seconds
                            counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds - \
                                                                         ellapsed_time_penalty_player_3_left_seconds
                        #    print("countdown time_penalty_player_3_left")
                            #
                        #
                        # *************  RIGHT **************
                        if running_time_penalty_player_1_right and \
                                counter_seconds_time_penalty_player_1_right == timepenalty_maximum_seconds and \
                                not time_penalty_player_1_right_initialized:
                            buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = 0
                            buffer_last_time_start_of_the_timepenalty_player1_right = datetime.now()
                        #    print("FIRST countdown time_penalty_player_1_right")
                        #    print("buffer start time_penalty_player_1_right initialized")
                            time_penalty_player_1_right_initialized = True
                            #
                        if running_time_penalty_player_1_right:
                            difference_date_time = datetime.now() - \
                                                   buffer_last_time_start_of_the_timepenalty_player1_right
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                            ellapsed_time_penalty_player_1_right_seconds = \
                                buffer_last_started_ellapsed_time_penalty_player_1_right_seconds + \
                                difference_date_time_in_seconds
                            counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds - \
                                                                          ellapsed_time_penalty_player_1_right_seconds
                        #    print("countdown time_penalty_player_1_right")
                            #
                        if running_time_penalty_player_2_right and \
                                counter_seconds_time_penalty_player_2_right == timepenalty_maximum_seconds and \
                                not time_penalty_player_2_right_initialized:
                            buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = 0
                            buffer_last_time_start_of_the_timepenalty_player2_right = datetime.now()
                        #    print("FIRST countdown time_penalty_player_2_right")
                        #    print("buffer start time_penalty_player_2_right initialized")
                            time_penalty_player_2_right_initialized = True
                            #
                        if running_time_penalty_player_2_right:
                            difference_date_time = \
                                datetime.now() - buffer_last_time_start_of_the_timepenalty_player2_right
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                            ellapsed_time_penalty_player_2_right_seconds = \
                                buffer_last_started_ellapsed_time_penalty_player_2_right_seconds + \
                                difference_date_time_in_seconds
                            counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds - \
                                                                          ellapsed_time_penalty_player_2_right_seconds
                        #    print("countdown time_penalty_player_2_right")
                            #
                        if running_time_penalty_player_3_right and \
                                counter_seconds_time_penalty_player_3_right == timepenalty_maximum_seconds and \
                                not time_penalty_player_3_right_initialized:
                            buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = 0
                            buffer_last_time_start_of_the_timepenalty_player3_right = datetime.now()
                        #    print("FIRST countdown time_penalty_player_3_right")
                        #    print("buffer start time_penalty_player_3_right initialized")
                            time_penalty_player_3_right_initialized = True
                            #
                        if running_time_penalty_player_3_right:
                            difference_date_time = datetime.now() - \
                                                   buffer_last_time_start_of_the_timepenalty_player3_right
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                            ellapsed_time_penalty_player_3_right_seconds = \
                                buffer_last_started_ellapsed_time_penalty_player_3_right_seconds + \
                                difference_date_time_in_seconds
                            counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds - \
                                                                          ellapsed_time_penalty_player_3_right_seconds
                        #    print("countdown time_penalty_player_3_right")
                            #

                    elif action_start_time_of_the_game_is_ACTIVE and counter_seconds_board<=0:

                        # game was not stopped but counter_seconds_board come to zero = typically end of a play period
                        # with action_start_time_of_the_game_is_ACTIVE = False we stop the game from here

                        #print("def run: countdown will be stopped because the counter was at zero")
                        #print("def run: all timepenalty will be stopped")
                        #print("def run: a button stop will be simulated")

                        counter_seconds_board = 0  # in case it would have been below 0 due to pause in timers

                        buffer_last_time_stop = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player1_left = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player2_left = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player3_left = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player1_right = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player2_right = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player3_right = datetime.now()
                    #
                        difference_date_time = buffer_last_time_stop - buffer_last_time_start
                        #print("def run: difference_date_time ", difference_date_time)
                        difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                          int(difference_date_time.seconds)
                        #print("def run: difference_date_time_in_seconds between buffer_last_time_start and now  ",
                        #      difference_date_time_in_seconds)
                        ellapsed_period_time_seconds = buffer_last_started_ellapsed_period_time_seconds + \
                                                       difference_date_time_in_seconds
                        counter_seconds_board = period_time_in_second - ellapsed_period_time_seconds
                        #print("def run: counter_seconds_board ", counter_seconds_board)
                        #
                        # update board timepenalty all players = constant
                        #
                        if running_time_penalty_player_1_left:
                            # for the first activation to start, time will not be calculated
                            if ellapsed_time_penalty_player_1_left_seconds == 0:
                                counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = 0
                        #        print("countdown time_penalty_player_1_left stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player1_left - \
                                                       buffer_last_time_start_of_the_timepenalty_player1_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_1_left_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_1_left_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_1_left stopped")
                                if ellapsed_time_penalty_player_1_left_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_1_left_seconds
                                else:
                                    running_time_penalty_player_1_left = False
                                    counter_seconds_time_penalty_player_1_left = 0
                                   #
                        if running_time_penalty_player_2_left:
                            # for the first activation to start, time will not be calculated
                            if ellapsed_time_penalty_player_2_left_seconds == 0:
                                counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = 0
                        #        print("countdown time_penalty_player_2_left stopped")
                            else:
                                     # what sense has this? default time during a STOP of the game.. logic to be analyzed
                    #                    else:
                    #                        if not stopped_special_time_sequence:
                    #                            counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player2_left - \
                                                       buffer_last_time_start_of_the_timepenalty_player2_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_2_left_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_2_left_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_2_left stopped")
                                if ellapsed_time_penalty_player_2_left_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_2_left_seconds
                                else:
                                    running_time_penalty_player_2_left = False
                                    counter_seconds_time_penalty_player_2_left = 0
                                    #
                        if running_time_penalty_player_3_left:
                            if ellapsed_time_penalty_player_3_left_seconds == 0:
                                counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = 0
                        #        print("countdown time_penalty_player_3_left stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player3_left - \
                                                       buffer_last_time_start_of_the_timepenalty_player3_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_3_left_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_3_left_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_3_left stopped")
                                if ellapsed_time_penalty_player_3_left_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_3_left_seconds
                                else:
                                    running_time_penalty_player_3_left = False
                                    counter_seconds_time_penalty_player_3_left = 0
                                    #
                                    #
                        if running_time_penalty_player_1_right:
                            if ellapsed_time_penalty_player_1_right_seconds == 0:
                                counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = 0
                        #        print("countdown time_penalty_player_1_right stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player1_right - \
                                                       buffer_last_time_start_of_the_timepenalty_player1_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_1_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_1_right_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_1_right stopped")
                                if ellapsed_time_penalty_player_1_right_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds - \
                                                                                  ellapsed_time_penalty_player_1_right_seconds
                                else:
                                    running_time_penalty_player_1_right = False
                                    counter_seconds_time_penalty_player_1_right = 0
                                #
                        if running_time_penalty_player_2_right:
                            if ellapsed_time_penalty_player_2_right_seconds == 0:
                                counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = 0
                        #        print("countdown time_penalty_player_2_right stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player2_right - \
                                                       buffer_last_time_start_of_the_timepenalty_player2_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_2_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_2_right_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_2_right stopped")
                                if ellapsed_time_penalty_player_2_right_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds - \
                                                                              ellapsed_time_penalty_player_2_right_seconds
                                else:
                                    running_time_penalty_player_2_right = False
                                    counter_seconds_time_penalty_player_2_right = 0
                        #
                        if running_time_penalty_player_3_right:
                            if ellapsed_time_penalty_player_3_right_seconds == 0:
                                counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = 0
                        #        print("countdown time_penalty_player_3_right stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player3_right - \
                                                       buffer_last_time_start_of_the_timepenalty_player3_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_3_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_3_right_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_3_right stopped")
                                if ellapsed_time_penalty_player_3_right_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds - \
                                                                                  ellapsed_time_penalty_player_3_right_seconds
                        #
                        #
                        # SECOND timer penalty timeout break
                        # probably no need to update the labels hereafter if the game was running and was stopped
                        # because it reached zero
                        #
                        if running_penalty or running_break or running_timeout:
                        #    print("datetime.now()  ", datetime.now())
                        #    print("buffer_time_start_special_time_sequence  ", buffer_time_start_special_time_sequence)
                            difference_date_time = datetime.now() - buffer_time_start_special_time_sequence
                        #    print("def run: difference_date_time -  buffer_time_start_special_time_sequence ",difference_date_time)
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                        #    print("def run: difference_date_time_in_seconds between buffer_time_start_special_time_sequence and now  "
                        #          , difference_date_time_in_seconds)
                            ellapsed_special_time_sequence_seconds = difference_date_time_in_seconds
                            counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds - \
                                                                    ellapsed_special_time_sequence_seconds
                        #    print("def run: counter_seconds_special_time_sequence ", counter_seconds_special_time_sequence)



                    else:
                        # action_start_time_of_the_game_is_ACTIVE = no, means the game is stopped from the stop
                        # button in the GUI and the countdown will be not running
                        # update board period time = constant
                        # only the special time sequence will be updated
                        #
                        #print("def run: countdown was stopped by the button stop when the countdown was >0")
                        #                        gtk.ToggleButton.set_active(True) = press the stop ??
                        #buffer_last_time_stop = datetime.now()
                        #buffer_last_time_stop_of_the_timepenalty_player1_left = datetime.now()
                        #buffer_last_time_stop_of_the_timepenalty_player2_left = datetime.now()
                        #buffer_last_time_stop_of_the_timepenalty_player3_left = datetime.now()
                        #buffer_last_time_stop_of_the_timepenalty_player1_right = datetime.now()
                        #buffer_last_time_stop_of_the_timepenalty_player2_right = datetime.now()
                        #buffer_last_time_stop_of_the_timepenalty_player3_right = datetime.now()
                        #

                        #  it makes any sense to update the counter seconds board? probably not
                        #
                        difference_date_time = buffer_last_time_stop - buffer_last_time_start
                        #print("def run: difference_date_time ", difference_date_time)
                        difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                          int(difference_date_time.seconds)
                        #print("def run: difference_date_time_in_seconds between buffer_last_time_start and now  ",
                        #      difference_date_time_in_seconds)
                        ellapsed_period_time_seconds = buffer_last_started_ellapsed_period_time_seconds + \
                                                       difference_date_time_in_seconds
                        counter_seconds_board = period_time_in_second - ellapsed_period_time_seconds
                        #print("def run: counter_seconds_board ", counter_seconds_board)


                        # update the labels timepenalty if no countdown?
                        # YES because the labels can change in case the board side switch is done when the
                        # game is stopped or during the break

                        #
                        # update board timepenalty all players = constant
                        #
                        if running_time_penalty_player_1_left:
                            # for the first activation to start, time will not be calculated
                            if ellapsed_time_penalty_player_1_left_seconds == 0:
                                counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = 0
                        #        print("countdown time_penalty_player_1_left stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player1_left - \
                                                       buffer_last_time_start_of_the_timepenalty_player1_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_1_left_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_1_left_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_1_left stopped")
                                if ellapsed_time_penalty_player_1_left_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_1_left_seconds
                                else:
                                    running_time_penalty_player_1_left = False
                                    counter_seconds_time_penalty_player_1_left = 0
                        #
                        if running_time_penalty_player_2_left:
                            # for the first activation to start, time will not be calculated
                            if ellapsed_time_penalty_player_2_left_seconds == 0:
                                counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = 0
                        #        print("countdown time_penalty_player_2_left stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player2_left - \
                                                       buffer_last_time_start_of_the_timepenalty_player2_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_2_left_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_2_left_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_2_left stopped")
                                if ellapsed_time_penalty_player_2_left_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_2_left_seconds
                                else:
                                    running_time_penalty_player_2_left = False
                                    counter_seconds_time_penalty_player_2_left = 0
                                    #
                        if running_time_penalty_player_3_left:
                            if ellapsed_time_penalty_player_3_left_seconds == 0:
                                counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = 0
                        #        print("countdown time_penalty_player_3_left stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player3_left - \
                                                       buffer_last_time_start_of_the_timepenalty_player3_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_3_left_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_3_left_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_3_left stopped")
                                if ellapsed_time_penalty_player_3_left_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_3_left_seconds
                                else:
                                    running_time_penalty_player_3_left = False
                                    counter_seconds_time_penalty_player_3_left = 0
                                #
                                #
                        if running_time_penalty_player_1_right:
                            if ellapsed_time_penalty_player_1_right_seconds == 0:
                                counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = 0
                        #        print("countdown time_penalty_player_1_right stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player1_right - \
                                                       buffer_last_time_start_of_the_timepenalty_player1_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_1_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_1_right_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_1_right stopped")
                                if ellapsed_time_penalty_player_1_right_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds - \
                                                                                  ellapsed_time_penalty_player_1_right_seconds
                                else:
                                    running_time_penalty_player_1_right = False
                                    counter_seconds_time_penalty_player_1_right = 0
                            #
                        if running_time_penalty_player_2_right:
                            if ellapsed_time_penalty_player_2_right_seconds == 0:
                                counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = 0
                        #        print("countdown time_penalty_player_2_right stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player2_right - \
                                                       buffer_last_time_start_of_the_timepenalty_player2_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_2_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_2_right_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_2_right stopped")
                                if ellapsed_time_penalty_player_2_right_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds - \
                                                                                  ellapsed_time_penalty_player_2_right_seconds
                                else:
                                    running_time_penalty_player_2_right = False
                                    counter_seconds_time_penalty_player_2_right = 0
                            #
                        if running_time_penalty_player_3_right:
                            if ellapsed_time_penalty_player_3_right_seconds == 0:
                                counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds
                                buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = 0
                        #        print("countdown time_penalty_player_3_right stopped")
                            else:
                                difference_date_time = buffer_last_time_stop_of_the_timepenalty_player3_right - \
                                                       buffer_last_time_start_of_the_timepenalty_player3_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_3_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_3_right_seconds + \
                                    difference_date_time_in_seconds
                                # stop counter of timepenalty if it went below 0
                        #        print("countdown time_penalty_player_3_right stopped")
                                if ellapsed_time_penalty_player_3_right_seconds <= timepenalty_maximum_seconds:
                                    counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds - \
                                                                                  ellapsed_time_penalty_player_3_right_seconds
                        #
                        #
                        # SECOND timer penalty timeout break
                        if running_penalty or running_break or running_timeout:
                        #    print("datetime.now()  ", datetime.now())
                        #    print("buffer_time_start_special_time_sequence  ", buffer_time_start_special_time_sequence)
                            difference_date_time = datetime.now() - buffer_time_start_special_time_sequence
                        #    print("def run: difference_date_time -  buffer_time_start_special_time_sequence ",
                        #          difference_date_time)
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                        #    print("def run: difference_date_time_in_seconds between buffer_time_start_special_time"
                        #          "_sequence and now  ", difference_date_time_in_seconds)
                            ellapsed_special_time_sequence_seconds = difference_date_time_in_seconds
                            counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds - \
                                                                    ellapsed_special_time_sequence_seconds
                        #    print("def run: counter_seconds_special_time_sequence ", counter_seconds_special_time_sequence)
                            #
                else:

                    # no watch stop -> different calculation logic
                    #

                    ellapsed_time_game = \
                        datetime.now() - start_time_of_the_game
                    ellapsed_time_game_in_seconds = int(ellapsed_time_game.days * 24 * 60 * 60) + \
                                                    int(ellapsed_time_game.seconds)

                    #print("def: run  ellapsed_time_game_in_seconds   ellapsed_period_time_seconds)   add_time_seconds", ellapsed_time_game_in_seconds, ellapsed_period_time_seconds, add_time_seconds)
                    #print("def: run  counter_seconds_board != period_time_in_second or game_started", counter_seconds_board, period_time_in_second, game_started)

                    if ((ellapsed_time_game_in_seconds - ellapsed_period_time_seconds) >= add_time_seconds):

                        if not now_dont_stop:
                            # add time already used up
                            # = no stop anymore
                            # = no timeout possible
                            # = no break can start
                            # = make here the final start
                            # = from now on, only a penalty could be done to the end

                            now_dont_stop = True
                            action_start_time_of_the_game_is_ACTIVE = True
                            buffer_last_time_start = datetime.now()
                            buffer_last_started_ellapsed_period_time_seconds = ellapsed_period_time_seconds
                            #
                            buffer_last_time_start_of_the_timepenalty_player1_left = datetime.now()
                            buffer_last_time_start_of_the_timepenalty_player2_left = datetime.now()
                            buffer_last_time_start_of_the_timepenalty_player3_left = datetime.now()
                            buffer_last_time_start_of_the_timepenalty_player1_right = datetime.now()
                            buffer_last_time_start_of_the_timepenalty_player2_right = datetime.now()
                            buffer_last_time_start_of_the_timepenalty_player3_right = datetime.now()
                            #
                            buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = \
                                ellapsed_time_penalty_player_1_left_seconds
                            buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = \
                                ellapsed_time_penalty_player_2_left_seconds
                            buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = \
                                ellapsed_time_penalty_player_3_left_seconds
                            buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = \
                                ellapsed_time_penalty_player_1_right_seconds
                            buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = \
                                ellapsed_time_penalty_player_2_right_seconds
                            buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = \
                                ellapsed_time_penalty_player_3_right_seconds
                            #



                        if counter_seconds_board > 0:
                                #
                                # game running (not stopped) and time not already down to zero.
                                # this is typically a running period of a game after a game was started
                                # it calculates here the board period time = countdown
                                #
                    #        print("def run: countdown running")
                            difference_date_time = datetime.now() - buffer_last_time_start
                    #        print("def run: difference_date_time ", difference_date_time)
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                    #        print(
                    #                "def run: difference_date_time_in_seconds between buffer_last_time_start and now  ",
                    #                difference_date_time_in_seconds)

                            if difference_date_time_in_seconds >= 0:
                                ellapsed_period_time_seconds = buffer_last_started_ellapsed_period_time_seconds + \
                                                                   difference_date_time_in_seconds
                                counter_seconds_board = period_time_in_second - ellapsed_period_time_seconds
                            else:
                    #            print("def run: difference_date_time_in_seconds identified negativ; set to zero  ")
                            #    difference_date_time_in_seconds = 0
                                counter_seconds_board = 0

                                # perhaps stop here all timepenalty
                    #        print("def run: counter_seconds_board ", counter_seconds_board)

                                #
                                # calculate board of all six timepenalty players = countdown
                                #
                                # *************   LEFT   ***************
                            if running_time_penalty_player_1_left and \
                                        counter_seconds_time_penalty_player_1_left == timepenalty_maximum_seconds and \
                                        not time_penalty_player_1_left_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player1_left = datetime.now()
                    #            print("FIRST countdown time_penalty_player_1_left")
                    #            print("buffer start time_penalty_player_1_left initialized")
                                time_penalty_player_1_left_initialized = True
                                #
                            if running_time_penalty_player_1_left:
                                difference_date_time = datetime.now() - \
                                                           buffer_last_time_start_of_the_timepenalty_player1_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_1_left_seconds = buffer_last_started_ellapsed_time_penalty_player_1_left_seconds + \
                                                                                  difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_1_left_seconds
                    #            print("countdown time_penalty_player_1_left")
                                #
                            if running_time_penalty_player_2_left and \
                                        counter_seconds_time_penalty_player_2_left == timepenalty_maximum_seconds and \
                                        not time_penalty_player_2_left_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player2_left = datetime.now()
                    #            print("FIRST countdown time_penalty_player_2_left")
                    #            print("buffer start time_penalty_player_2_left initialized")
                                time_penalty_player_2_left_initialized = True
                                #
                            if running_time_penalty_player_2_left:
                                difference_date_time = \
                                        datetime.now() - buffer_last_time_start_of_the_timepenalty_player2_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_2_left_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_2_left_seconds + \
                                        difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_2_left_seconds
                    #            print("countdown time_penalty_player_2_left")
                                    #
                            if running_time_penalty_player_3_left and \
                                        counter_seconds_time_penalty_player_3_left == timepenalty_maximum_seconds and \
                                        not time_penalty_player_3_left_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player3_left = datetime.now()
                    #            print("FIRST countdown time_penalty_player_3_left")
                    #            print("buffer start time_penalty_player_3_left initialized")
                                time_penalty_player_3_left_initialized = True
                                    #
                            if running_time_penalty_player_3_left:
                                difference_date_time = datetime.now() - \
                                                           buffer_last_time_start_of_the_timepenalty_player3_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_3_left_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_3_left_seconds + \
                                        difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds - \
                                                                                 ellapsed_time_penalty_player_3_left_seconds
                    #            print("countdown time_penalty_player_3_left")
                                    #
                                #
                                # *************  RIGHT **************
                            if running_time_penalty_player_1_right and \
                                        counter_seconds_time_penalty_player_1_right == timepenalty_maximum_seconds and \
                                        not time_penalty_player_1_right_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player1_right = datetime.now()
                    #            print("FIRST countdown time_penalty_player_1_right")
                    #            print("buffer start time_penalty_player_1_right initialized")
                                time_penalty_player_1_right_initialized = True
                                    #
                            if running_time_penalty_player_1_right:
                                difference_date_time = datetime.now() - \
                                                           buffer_last_time_start_of_the_timepenalty_player1_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_1_right_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_1_right_seconds + \
                                        difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds - \
                                                                                  ellapsed_time_penalty_player_1_right_seconds
                    #            print("countdown time_penalty_player_1_right")
                                    #
                            if running_time_penalty_player_2_right and \
                                        counter_seconds_time_penalty_player_2_right == timepenalty_maximum_seconds and \
                                        not time_penalty_player_2_right_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player2_right = datetime.now()
                    #            print("FIRST countdown time_penalty_player_2_right")
                    #            print("buffer start time_penalty_player_2_right initialized")
                                time_penalty_player_2_right_initialized = True
                                    #
                            if running_time_penalty_player_2_right:
                                difference_date_time = \
                                        datetime.now() - buffer_last_time_start_of_the_timepenalty_player2_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_2_right_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_2_right_seconds + \
                                        difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds - \
                                                                                  ellapsed_time_penalty_player_2_right_seconds
                    #            print("countdown time_penalty_player_2_right")
                                    #
                            if running_time_penalty_player_3_right and \
                                    counter_seconds_time_penalty_player_3_right == timepenalty_maximum_seconds and \
                                        not time_penalty_player_3_right_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player3_right = datetime.now()
                    #            print("FIRST countdown time_penalty_player_3_right")
                    #            print("buffer start time_penalty_player_3_right initialized")
                                time_penalty_player_3_right_initialized = True
                                    #
                            if running_time_penalty_player_3_right:
                                difference_date_time = datetime.now() - \
                                                           buffer_last_time_start_of_the_timepenalty_player3_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_3_right_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_3_right_seconds + \
                                        difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds - \
                                                                                  ellapsed_time_penalty_player_3_right_seconds
                    #            print("countdown time_penalty_player_3_right")
                                    #

                            if running_penalty or running_break or running_timeout:
                    #            print("datetime.now()  ", datetime.now())
                    #            print("buffer_time_start_special_time_sequence  ",
                    #                      buffer_time_start_special_time_sequence)
                                difference_date_time = datetime.now() - buffer_time_start_special_time_sequence
                    #            print("def run: difference_date_time -  buffer_time_start_special_time_sequence ",
                    #                      difference_date_time)
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                    #            print(
                    #                    "def run: difference_date_time_in_seconds between buffer_time_start_special_time_sequence and now  "
                    #                    , difference_date_time_in_seconds)
                                ellapsed_special_time_sequence_seconds = difference_date_time_in_seconds
                                counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds - \
                                                                            ellapsed_special_time_sequence_seconds
                    #            print("def run: counter_seconds_special_time_sequence ",
                    #                      counter_seconds_special_time_sequence)

                        elif counter_seconds_board <= 0:

                                # game was not stopped but counter_seconds_board come to zero = typically end of a play period
                                # any penalty time will run till the end

                    #        print("def run: countdown was stopped because the counter was at zero")
                    #        print("def run: all timepenalty will be stopped")

                            if not running_penalty: # then the game can be stopped. Else it runs till the end.

                                counter_seconds_board = 0  # in case it would have been below 0 due to pause in timers

                                buffer_last_time_stop = datetime.now()
                                buffer_last_time_stop_of_the_timepenalty_player1_left = datetime.now()
                                buffer_last_time_stop_of_the_timepenalty_player2_left = datetime.now()
                                buffer_last_time_stop_of_the_timepenalty_player3_left = datetime.now()
                                buffer_last_time_stop_of_the_timepenalty_player1_right = datetime.now()
                                buffer_last_time_stop_of_the_timepenalty_player2_right = datetime.now()
                                buffer_last_time_stop_of_the_timepenalty_player3_right = datetime.now()
                                #

                            #difference_date_time = buffer_last_time_stop - buffer_last_time_start
                            #print("def run: difference_date_time ", difference_date_time)
                            #difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                            #                                     int(difference_date_time.seconds)
                            #print(
                            #        "def run: difference_date_time_in_seconds between buffer_last_time_start and now  ",
                            #        difference_date_time_in_seconds)
                            #ellapsed_period_time_seconds = buffer_last_started_ellapsed_period_time_seconds + \
                            #                                   difference_date_time_in_seconds
                            #counter_seconds_board = period_time_in_second - ellapsed_period_time_seconds

                            counter_seconds_board = 0  # in case it would have been below 0 due to pause in timers

                    #        print("def run: counter_seconds_board ", counter_seconds_board)
                                #
                                #
                                # SECOND timer penalty
                            if running_penalty:
                    #            print("datetime.now()  ", datetime.now())
                    #            print("buffer_time_start_special_time_sequence  ",
                    #                      buffer_time_start_special_time_sequence)
                                difference_date_time = datetime.now() - buffer_time_start_special_time_sequence
                    #            print("def run: difference_date_time -  buffer_time_start_special_time_sequence ",
                    #                      difference_date_time)
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                    #            print(
                    #                    "def run: difference_date_time_in_seconds between buffer_time_start_special_time_sequence and now  "
                    #                    , difference_date_time_in_seconds)
                                ellapsed_special_time_sequence_seconds = difference_date_time_in_seconds
                                counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds - \
                                                                            ellapsed_special_time_sequence_seconds
                    #            print("def run: counter_seconds_special_time_sequence ",
                    #                      counter_seconds_special_time_sequence)

                                if counter_seconds_special_time_sequence < 0:  # counter comes to zero, stop everything
                                    running_penalty = False


                    else:

                        # start-stop logic fine because the allowed add_time for stops was not used up

                        if action_start_time_of_the_game_is_ACTIVE and counter_seconds_board > 0:
                            #
                            # game running (not stopped) and time not already down to zero.
                            # this is typically a running period of a game after a game was started
                            # it calculates here the board period time = countdown
                            #
                    #        print("def run: countdown running")
                            difference_date_time = datetime.now() - buffer_last_time_start
                    #        print("def run: difference_date_time ", difference_date_time)
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                    #        print("def run: difference_date_time_in_seconds between buffer_last_time_start and now  ",
                    #              difference_date_time_in_seconds)

                            if difference_date_time_in_seconds >= 0:
                                ellapsed_period_time_seconds = buffer_last_started_ellapsed_period_time_seconds + \
                                                               difference_date_time_in_seconds
                                counter_seconds_board = period_time_in_second - ellapsed_period_time_seconds
                            else:
                    #            print("def run: difference_date_time_in_seconds identified negativ; set to zero  ")
                                #    difference_date_time_in_seconds = 0
                                counter_seconds_board = 0

                            # perhaps stop here all timepenalty
                    #        print("def run: counter_seconds_board ", counter_seconds_board)

                            #
                            # calculate board of all six timepenalty players = countdown
                            #
                            # *************   LEFT   ***************
                            if running_time_penalty_player_1_left and \
                                    counter_seconds_time_penalty_player_1_left == timepenalty_maximum_seconds and \
                                    not time_penalty_player_1_left_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player1_left = datetime.now()
                    #            print("FIRST countdown time_penalty_player_1_left")
                    #            print("buffer start time_penalty_player_1_left initialized")
                                time_penalty_player_1_left_initialized = True
                            #
                            if running_time_penalty_player_1_left:
                                difference_date_time = datetime.now() - \
                                                       buffer_last_time_start_of_the_timepenalty_player1_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_1_left_seconds = buffer_last_started_ellapsed_time_penalty_player_1_left_seconds + \
                                                                              difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds - \
                                                                             ellapsed_time_penalty_player_1_left_seconds
                    #            print("countdown time_penalty_player_1_left")
                            #
                            if running_time_penalty_player_2_left and \
                                    counter_seconds_time_penalty_player_2_left == timepenalty_maximum_seconds and \
                                    not time_penalty_player_2_left_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player2_left = datetime.now()
                    #            print("FIRST countdown time_penalty_player_2_left")
                    #            print("buffer start time_penalty_player_2_left initialized")
                                time_penalty_player_2_left_initialized = True
                            #
                            if running_time_penalty_player_2_left:
                                difference_date_time = \
                                    datetime.now() - buffer_last_time_start_of_the_timepenalty_player2_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_2_left_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_2_left_seconds + \
                                    difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds - \
                                                                             ellapsed_time_penalty_player_2_left_seconds
                    #            print("countdown time_penalty_player_2_left")
                                #
                            if running_time_penalty_player_3_left and \
                                    counter_seconds_time_penalty_player_3_left == timepenalty_maximum_seconds and \
                                    not time_penalty_player_3_left_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player3_left = datetime.now()
                    #            print("FIRST countdown time_penalty_player_3_left")
                    #            print("buffer start time_penalty_player_3_left initialized")
                                time_penalty_player_3_left_initialized = True
                                #
                            if running_time_penalty_player_3_left:
                                difference_date_time = datetime.now() - \
                                                       buffer_last_time_start_of_the_timepenalty_player3_left
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_3_left_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_3_left_seconds + \
                                    difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds - \
                                                                             ellapsed_time_penalty_player_3_left_seconds
                    #            print("countdown time_penalty_player_3_left")
                                #
                            #
                            # *************  RIGHT **************
                            if running_time_penalty_player_1_right and \
                                    counter_seconds_time_penalty_player_1_right == timepenalty_maximum_seconds and \
                                    not time_penalty_player_1_right_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player1_right = datetime.now()
                    #            print("FIRST countdown time_penalty_player_1_right")
                    #            print("buffer start time_penalty_player_1_right initialized")
                                time_penalty_player_1_right_initialized = True
                                #
                            if running_time_penalty_player_1_right:
                                difference_date_time = datetime.now() - \
                                                       buffer_last_time_start_of_the_timepenalty_player1_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_1_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_1_right_seconds + \
                                    difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds - \
                                                                              ellapsed_time_penalty_player_1_right_seconds
                    #            print("countdown time_penalty_player_1_right")
                                #
                            if running_time_penalty_player_2_right and \
                                    counter_seconds_time_penalty_player_2_right == timepenalty_maximum_seconds and \
                                    not time_penalty_player_2_right_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player2_right = datetime.now()
                    #            print("FIRST countdown time_penalty_player_2_right")
                    #            print("buffer start time_penalty_player_2_right initialized")
                                time_penalty_player_2_right_initialized = True
                                #
                            if running_time_penalty_player_2_right:
                                difference_date_time = \
                                    datetime.now() - buffer_last_time_start_of_the_timepenalty_player2_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_2_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_2_right_seconds + \
                                    difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds - \
                                                                              ellapsed_time_penalty_player_2_right_seconds
                    #            print("countdown time_penalty_player_2_right")
                                #
                            if running_time_penalty_player_3_right and \
                                    counter_seconds_time_penalty_player_3_right == timepenalty_maximum_seconds and \
                                    not time_penalty_player_3_right_initialized:
                                buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = 0
                                buffer_last_time_start_of_the_timepenalty_player3_right = datetime.now()
                    #            print("FIRST countdown time_penalty_player_3_right")
                    #            print("buffer start time_penalty_player_3_right initialized")
                                time_penalty_player_3_right_initialized = True
                                #
                            if running_time_penalty_player_3_right:
                                difference_date_time = datetime.now() - \
                                                       buffer_last_time_start_of_the_timepenalty_player3_right
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                                ellapsed_time_penalty_player_3_right_seconds = \
                                    buffer_last_started_ellapsed_time_penalty_player_3_right_seconds + \
                                    difference_date_time_in_seconds
                                counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds - \
                                                                              ellapsed_time_penalty_player_3_right_seconds
                    #            print("countdown time_penalty_player_3_right")
                                #

                        elif action_start_time_of_the_game_is_ACTIVE and counter_seconds_board <= 0:

                            # game was not stopped but counter_seconds_board come to zero = typically end of a play period
                            # action_start_time_of_the_game_is_ACTIVE = False   # we stop the game from here
                            # we should not stop from here?

                    #        print("def run: countdown was stopped because the counter was at zero")
                    #        print("def run: all timepenalty will be stopped")
                    #        print("def run: a button stop will be simulated")

                            counter_seconds_board = 0  # in case it would have been below 0 due to pause in timers

                            buffer_last_time_stop = datetime.now()
                            buffer_last_time_stop_of_the_timepenalty_player1_left = datetime.now()
                            buffer_last_time_stop_of_the_timepenalty_player2_left = datetime.now()
                            buffer_last_time_stop_of_the_timepenalty_player3_left = datetime.now()
                            buffer_last_time_stop_of_the_timepenalty_player1_right = datetime.now()
                            buffer_last_time_stop_of_the_timepenalty_player2_right = datetime.now()
                            buffer_last_time_stop_of_the_timepenalty_player3_right = datetime.now()
                            #
                            difference_date_time = buffer_last_time_stop - buffer_last_time_start
                    #        print("def run: difference_date_time ", difference_date_time)
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                    #        print("def run: difference_date_time_in_seconds between buffer_last_time_start and now  ",
                    #              difference_date_time_in_seconds)
                            ellapsed_period_time_seconds = buffer_last_started_ellapsed_period_time_seconds + \
                                                           difference_date_time_in_seconds
                            counter_seconds_board = period_time_in_second - ellapsed_period_time_seconds
                    #        print("def run: counter_seconds_board ", counter_seconds_board)
                            #
                            # update board timepenalty all players = constant
                            #
                            if running_time_penalty_player_1_left:
                                # for the first activation to start, time will not be calculated
                                if ellapsed_time_penalty_player_1_left_seconds == 0:
                                    counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds
                                    buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = 0
                    #                print("countdown time_penalty_player_1_left stopped")
                                else:
                                    difference_date_time = buffer_last_time_stop_of_the_timepenalty_player1_left - \
                                                           buffer_last_time_start_of_the_timepenalty_player1_left
                                    difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                    ellapsed_time_penalty_player_1_left_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_1_left_seconds + \
                                        difference_date_time_in_seconds
                                    # stop counter of timepenalty if it went below 0
                    #                print("countdown time_penalty_player_1_left stopped")
                                    if ellapsed_time_penalty_player_1_left_seconds <= timepenalty_maximum_seconds:
                                        counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds - \
                                                                                     ellapsed_time_penalty_player_1_left_seconds
                                    else:
                                        running_time_penalty_player_1_left = False
                                        counter_seconds_time_penalty_player_1_left = 0
                                    #
                            if running_time_penalty_player_2_left:
                                # for the first activation to start, time will not be calculated
                                if ellapsed_time_penalty_player_2_left_seconds == 0:
                                    counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds
                                    buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = 0
                    #                print("countdown time_penalty_player_2_left stopped")
                                else:
                                    # what sense has this? default time during a STOP of the game.. logic to be analyzed
                                    #                    else:
                                    #                        if not stopped_special_time_sequence:
                                    #                            counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds
                                    difference_date_time = buffer_last_time_stop_of_the_timepenalty_player2_left - \
                                                           buffer_last_time_start_of_the_timepenalty_player2_left
                                    difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                    ellapsed_time_penalty_player_2_left_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_2_left_seconds + \
                                        difference_date_time_in_seconds
                                    # stop counter of timepenalty if it went below 0
                    #                print("countdown time_penalty_player_2_left stopped")
                                    if ellapsed_time_penalty_player_2_left_seconds <= timepenalty_maximum_seconds:
                                        counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds - \
                                                                                     ellapsed_time_penalty_player_2_left_seconds
                                    else:
                                        running_time_penalty_player_2_left = False
                                        counter_seconds_time_penalty_player_2_left = 0
                                        #
                            if running_time_penalty_player_3_left:
                                if ellapsed_time_penalty_player_3_left_seconds == 0:
                                    counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds
                                    buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = 0
                    #                print("countdown time_penalty_player_3_left stopped")
                                else:
                                    difference_date_time = buffer_last_time_stop_of_the_timepenalty_player3_left - \
                                                           buffer_last_time_start_of_the_timepenalty_player3_left
                                    difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                    ellapsed_time_penalty_player_3_left_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_3_left_seconds + \
                                        difference_date_time_in_seconds
                                    # stop counter of timepenalty if it went below 0
                    #                print("countdown time_penalty_player_3_left stopped")
                                    if ellapsed_time_penalty_player_3_left_seconds <= timepenalty_maximum_seconds:
                                        counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds - \
                                                                                     ellapsed_time_penalty_player_3_left_seconds
                                    else:
                                        running_time_penalty_player_3_left = False
                                        counter_seconds_time_penalty_player_3_left = 0
                                        #
                                        #
                            if running_time_penalty_player_1_right:
                                if ellapsed_time_penalty_player_1_right_seconds == 0:
                                    counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds
                                    buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = 0
                    #                print("countdown time_penalty_player_1_right stopped")
                                else:
                                    difference_date_time = buffer_last_time_stop_of_the_timepenalty_player1_right - \
                                                           buffer_last_time_start_of_the_timepenalty_player1_right
                                    difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                    ellapsed_time_penalty_player_1_right_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_1_right_seconds + \
                                        difference_date_time_in_seconds
                                    # stop counter of timepenalty if it went below 0
                    #                print("countdown time_penalty_player_1_right stopped")
                                    if ellapsed_time_penalty_player_1_right_seconds <= timepenalty_maximum_seconds:
                                        counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds - \
                                                                                      ellapsed_time_penalty_player_1_right_seconds
                                    else:
                                        running_time_penalty_player_1_right = False
                                        counter_seconds_time_penalty_player_1_right = 0
                                    #
                            if running_time_penalty_player_2_right:
                                if ellapsed_time_penalty_player_2_right_seconds == 0:
                                    counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds
                                    buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = 0
                    #                print("countdown time_penalty_player_2_right stopped")
                                else:
                                    difference_date_time = buffer_last_time_stop_of_the_timepenalty_player2_right - \
                                                           buffer_last_time_start_of_the_timepenalty_player2_right
                                    difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                    ellapsed_time_penalty_player_2_right_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_2_right_seconds + \
                                        difference_date_time_in_seconds
                                    # stop counter of timepenalty if it went below 0
                    #                print("countdown time_penalty_player_2_right stopped")
                                    if ellapsed_time_penalty_player_2_right_seconds <= timepenalty_maximum_seconds:
                                        counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds - \
                                                                                      ellapsed_time_penalty_player_2_right_seconds
                                    else:
                                        running_time_penalty_player_2_right = False
                                        counter_seconds_time_penalty_player_2_right = 0
                            #
                            if running_time_penalty_player_3_right:
                                if ellapsed_time_penalty_player_3_right_seconds == 0:
                                    counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds
                                    buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = 0
                    #                print("countdown time_penalty_player_3_right stopped")
                                else:
                                    difference_date_time = buffer_last_time_stop_of_the_timepenalty_player3_right - \
                                                           buffer_last_time_start_of_the_timepenalty_player3_right
                                    difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                      int(difference_date_time.seconds)
                                    ellapsed_time_penalty_player_3_right_seconds = \
                                        buffer_last_started_ellapsed_time_penalty_player_3_right_seconds + \
                                        difference_date_time_in_seconds
                                    # stop counter of timepenalty if it went below 0
                    #                print("countdown time_penalty_player_3_right stopped")
                                    if ellapsed_time_penalty_player_3_right_seconds <= timepenalty_maximum_seconds:
                                        counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds - \
                                                                                      ellapsed_time_penalty_player_3_right_seconds
                            #
                            #
                            # SECOND timer penalty timeout break
                            if running_penalty or running_break or running_timeout:
                    #            print("datetime.now()  ", datetime.now())
                    #            print("buffer_time_start_special_time_sequence  ",
                    #                  buffer_time_start_special_time_sequence)
                                difference_date_time = datetime.now() - buffer_time_start_special_time_sequence
                    #            print("def run: difference_date_time -  buffer_time_start_special_time_sequence ",
                    #                  difference_date_time)
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                    #            print(
                    #                "def run: difference_date_time_in_seconds between buffer_time_start_special_time_sequence and now  "
                    #                , difference_date_time_in_seconds)
                                ellapsed_special_time_sequence_seconds = difference_date_time_in_seconds
                                counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds - \
                                                                        ellapsed_special_time_sequence_seconds
                    #            print("def run: counter_seconds_special_time_sequence ",
                    #                  counter_seconds_special_time_sequence)



                        else:
                            # action_start_time_of_the_game_is_ACTIVE = no, means the game is stopped from the stop
                            # button in the GUI and the countdown not running
                            # update board period time = constant
                            # only the special time sequence will be updated
                            #
                    #        print("def run: countdown was stopped by the button stop when the countdown was >0")
                            #                        gtk.ToggleButton.set_active(True) = press the stop ??
                            # buffer_last_time_stop = datetime.now()
                            # buffer_last_time_stop_of_the_timepenalty_player1_left = datetime.now()
                            # buffer_last_time_stop_of_the_timepenalty_player2_left = datetime.now()
                            # buffer_last_time_stop_of_the_timepenalty_player3_left = datetime.now()
                            # buffer_last_time_stop_of_the_timepenalty_player1_right = datetime.now()
                            # buffer_last_time_stop_of_the_timepenalty_player2_right = datetime.now()
                            # buffer_last_time_stop_of_the_timepenalty_player3_right = datetime.now()
                            #

                            #  it makes any sense to update the counter seconds board? probably not
                            difference_date_time = buffer_last_time_stop - buffer_last_time_start
                    #        print("def run: difference_date_time ", difference_date_time)
                            difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                              int(difference_date_time.seconds)
                    #        print("def run: difference_date_time_in_seconds between buffer_last_time_start and now  ",
                    #              difference_date_time_in_seconds)
                            ellapsed_period_time_seconds = buffer_last_started_ellapsed_period_time_seconds + \
                                                           difference_date_time_in_seconds
                            counter_seconds_board = period_time_in_second - ellapsed_period_time_seconds
                    #        print("def run: counter_seconds_board ", counter_seconds_board)

                            #
                            # SECOND timer penalty timeout break
                            if running_penalty or running_break or running_timeout:
                    #            print("datetime.now()  ", datetime.now())
                    #            print("buffer_time_start_special_time_sequence  ",
                    #                  buffer_time_start_special_time_sequence)
                                difference_date_time = datetime.now() - buffer_time_start_special_time_sequence
                    #            print("def run: difference_date_time -  buffer_time_start_special_time_sequence ",
                    #                  difference_date_time)
                                difference_date_time_in_seconds = int(difference_date_time.days * 24 * 60 * 60) + \
                                                                  int(difference_date_time.seconds)
                    #            print("def run: difference_date_time_in_seconds between buffer_time_start_special_time"
                    #                  "_sequence and now  ", difference_date_time_in_seconds)
                                ellapsed_special_time_sequence_seconds = difference_date_time_in_seconds
                                counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds - \
                                                                        ellapsed_special_time_sequence_seconds
                    #            print("def run: counter_seconds_special_time_sequence ",
                    #                  counter_seconds_special_time_sequence)
                                #
                #
            else:
                # game NOT started
                buffer_last_started_ellapsed_period_time_seconds = 0
                counter_seconds_board = period_time_in_second

            #print("update_timers in run all 0.2s")
            self.emit("update_timers")  # signal "update" absetzen
            time.sleep(0.2)


#
thread_time_control = _time_controlThread()


#
class GUIclass:
    #
    def exit_action(self, widget, data=None):
        #print("**************")
        #print("**          **")
        #print("**  exit?   **")
        #print("**          **")
        #print("**************")
        self.exitdialog.show()

    def exit_confirmed(self, widget, data=None):
        global game_not_cancelled

        self.exitdialog.hide()
        #print("**********************")
        #print("**                  **")
        #print("**  exit confirmed  **")
        #print("**                  **")
        #print("**********************")
        game_not_cancelled = False

        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            now = datetime.now()
            logfile_game_handler.write("************* control board activity **************\n")
            logfile_game_handler.write("exit scoreboard\n")
            logfile_game_handler.write("  at time     : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
        #    logfile_game_handler.write("  at countdown: %s\n" % (self.label_control_current_time.get_text()))
            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()
            thread_time_control.cancelled = True

        gtk.main_quit()
        return True

    def exit_aborted(self, widget, data=None):
        self.exitdialog.hide()

    def watch_stop_yes(self, widget, data=None):

        global logfile_game
        global add_time_seconds
        global watch_stop
        global running_second_period_time
        global running_first_period_time
        global now_dont_stop
        global action_start_time_of_the_game_is_ACTIVE

        # it means a standard game with start / stop etc.
        #print("************************************")
        #print("**                                **")
        #print("**  standard watch start / stop   **")
        #print("**                                **")
        #print("************************************")

        add_time_seconds = 0
        watch_stop = True
        now_dont_stop = False
        running_first_period_time = False
        running_second_period_time = False
        action_start_time_of_the_game_is_ACTIVE = False

        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            now = datetime.now()
            logfile_game_handler.write("************* control board activity **************\n")
            logfile_game_handler.write("standard watch runnning choosen\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "standard watch runnning choosen\n")

            logfile_game_handler.write("  at time     : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "  at time     : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

        #    logfile_game_handler.write("  at countdown: %s\n" % (self.label_control_current_time.get_text()))
            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()

    def watch_stop_no(self, widget, data=None):

        global logfile_game
        global add_time_seconds
        global watch_stop
        global running_second_period_time
        global running_first_period_time
        global now_dont_stop
        global action_start_time_of_the_game_is_ACTIVE

        # it means no timeout, penalty without stopping the clock,.. no game interruption after start.
        # the main stop button must stay activ if a stop for reset is requested
        # timepenalty are not stopped by a free
        #print("***********************")
        #print("**                   **")
        #print("**  non stop watch   **")
        #print("**                   **")
        #print("***********************")

        now_dont_stop = False
        watch_stop = False
        running_first_period_time = False
        running_second_period_time = False
        action_start_time_of_the_game_is_ACTIVE = False

        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            now = datetime.now()
            logfile_game_handler.write("************* control board activity **************\n")
            logfile_game_handler.write("non stop watch runnning mode choosen\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "non stop watch runnning mode choosen\n")

            logfile_game_handler.write("stop button deactivated till countdown at zero\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "stop button deactivated till countdown at zero\n")

            logfile_game_handler.write("  at time     : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "  at time     : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

    #        logfile_game_handler.write("  at countdown: %s\n" % (self.label_control_current_time.get_text()))
            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()

        add_time_seconds = 60*int(self.spinbutton_add_time.get_value())

    def logging_on(self, widget, data=None):
        global logfile_game
        global logfile_game_handler
        if self.button_log_functionality_on.get_active():
            # when clicking on the stop main button, a dialog window will appear
            #print("************************************")
            #print("**                                **")
            #print("**  logging activated             **")
            #print("**  - log file written            **")
            #print("**  - comment/writing of events   **")
            #print("**  - screen log                  **")
            #print("**                                **")
            #print("************************************")
            self.entry_log_filename.set_property("editable",False)
            self.entry_log_filename.set_sensitive(False)
            self.button_logview_hide.set_active(True)
            logfile_game = ""
            logfile_game = self.entry_log_filename.get_text()
            if logfile_game == "":
                logfile_game = str(self.entry_tournament_name.get_text()) + '_' \
                               + str(self.entry_team_blue_name.get_text()) + '_' \
                               + str(self.entry_team_white_name.get_text()) + '.log'
            else:
                if logfile_game.find('.log') == -1:  # -1 will be returned when a is not in b
                    logfile_game = logfile_game + '.log'
            logfile_game_handler = open(logfile_game, 'w')

            logfile_game_handler.write("***************************************************\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "***************************************************\n")

            logfile_game_handler.write("*          scoreboard UWR                         *\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "*          scoreboard UWR                         *\n")

            logfile_game_handler.write("*          underwaterrugby game reporting         *\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "*          underwaterrugby game reporting         *\n")

            logfile_game_handler.write("*          pascaldagornet@yahoo.de                *\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "*          pascaldagornet@yahoo.de                *\n")

            logfile_game_handler.write("***************************************************\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "***************************************************\n")
            now = datetime.now()
            logfile_game_handler.write("date           : %s\n" % (str(now.strftime("%Y-%m-%d"))))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                  "date           : %s\n" % (str(now.strftime("%Y-%m-%d"))))
            logfile_game_handler.write("tournament name: %s\n" % (str(self.entry_tournament_name.get_text())))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                  "tournament name: %s\n" % (str(self.entry_tournament_name.get_text())))
            logfile_game_handler.write("contact person : %s\n" % (str(self.entry_tournament_contact.get_text())))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                  "contact person : %s\n" % (str(self.entry_tournament_contact.get_text())))
    #        logfile_game_handler.write("team blue:  %s\n" % (str(self.entry_team_blue_name.get_text())))
    #        logfile_game_handler.write("team white: %s\n" % (str(self.entry_team_white_name.get_text())))
            logfile_game_handler.write("***************************************************\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "***************************************************\n")
            logfile_game_handler.close()

    def view_logfile(self, widget, data=None):
        if self.button_log_functionality_on.get_active() and self.button_logview_pn.get_active():
            self.logviewwindow.show()
            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),"\n")
            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),"new log window checking\n")

    def hide_logfile(self, widget, data=None):
        if self.button_log_functionality_on.get_active():
            self.logviewwindow.hide()

    def hide_logwindow(self, widget, data=None):
        if self.button_log_functionality_on.get_active():
            self.logviewwindow.hide()
            self.button_logview_hide.set_active(True)

    def logging_off(self, widget, data=None):
        #
        '''no writing into a file, no dialog window will come up
        A confirmation dialog will come up; to be sure it was the clear request and not
        an uncontrolled  clicking deactivating the logging'''
        #
        if self.button_log_functionality_off.get_active():
            #print("**********************************************")
            #print("**                                          **")
            #print("**  logging deactivated                     **")
            #print("**  - no log file written                   **")
            #print("**  - no comment/writing of events          **")
            #print("**  only screen log (copy/paste possible)   **")
            #print("**                                          **")
            #print("**********************************************")
            self.logoffdialog.show()

    def logoff_confirmed(self, widget, data=None):
        global logfile_game
        '''NO writing of the events into a file.
        NO dialog window will come up anymore.
        The confirmation dialog will close after it was confirmed the clicking deactivating the logging'''
        #
        self.entry_log_filename.set_property("editable", True)
        self.entry_log_filename.set_sensitive(True)
        self.logoffdialog.hide()
        logfile_game_handler = open(logfile_game, 'a')
        now = datetime.now()
        logfile_game_handler.write("************* control board activity **************\n")
        logfile_game_handler.write("logging deactivation confirmed\n")
        logfile_game_handler.write("  at time     : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
        #logfile_game_handler.write("  at countdown: %s\n" % (self.label_control_current_time.get_text()))
        logfile_game_handler.write("***************************************************\n")
        logfile_game_handler.close()

    def logoff_aborted(self, widget, data=None):
        self.button_log_functionality_on.set_active(True)
        self.logoffdialog.hide()

    def view_window_on(self, widget, data=None):
        global left_team_is_blue

        if self.button_type_view_invertedcontrolview.get_active() \
                and self.button_separate_game_view_on.get_active():
            self.label_view_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_right.get_text())
            self.label_view_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_right.get_text())
            self.label_view_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_right.get_text())
            self.label_view_name_penalty_player_1_right.set_text(self.entry_name_penalty_player_1_left.get_text())
            self.label_view_name_penalty_player_2_right.set_text(self.entry_name_penalty_player_2_left.get_text())
            self.label_view_name_penalty_player_3_right.set_text(self.entry_name_penalty_player_3_left.get_text())
        else:
            self.label_view_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_left.get_text())
            self.label_view_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_left.get_text())
            self.label_view_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_left.get_text())
            self.label_view_name_penalty_player_1_right.set_text(self.entry_name_penalty_player_1_right.get_text())
            self.label_view_name_penalty_player_2_right.set_text(self.entry_name_penalty_player_2_right.get_text())
            self.label_view_name_penalty_player_3_right.set_text(self.entry_name_penalty_player_3_right.get_text())

        if left_team_is_blue:  # left team is blue in the control view

            if self.button_type_view_copycontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                             gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 1, 1))
                self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

                self.label_view_team_name_left.set_text(self.entry_team_blue_name.get_text())
                self.label_view_team_name_right.set_text(self.entry_team_white_name.get_text())

                self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

            else:
                self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                             gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(0, 0, 1, 1))
                self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

                self.label_view_team_name_right.set_text(self.entry_team_blue_name.get_text())
                self.label_view_team_name_left.set_text(self.entry_team_white_name.get_text())

                self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

        else:

            if self.button_type_view_copycontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                             gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(1, 1, 1, 1))
                self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                self.label_view_team_name_right.set_text(self.entry_team_blue_name.get_text())
                self.label_view_team_name_left.set_text(self.entry_team_white_name.get_text())

                self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

            else:
                self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                             gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(1, 1, 1, 1))
                self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                self.label_view_team_name_left.set_text(self.entry_team_blue_name.get_text())
                self.label_view_team_name_right.set_text(self.entry_team_white_name.get_text())

                self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

        self.viewwindow.show()

    def view_window_off(self, widget, data=None):
        #print("************************************")
        #print("**                                **")
        #print("**  separate view window closed   **")
        #print("**                                **")
        #print("************************************")
        self.viewwindow.hide()

    def copied_view(self, widget, data=None):
        if self.button_separate_game_view_on.get_active():
            #print("******************************")
            #print("**                          **")
            #print("**  copied view window on   **")
            #print("**                          **")
            #print("******************************")

            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_right.get_text())
                self.label_view_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_right.get_text())
                self.label_view_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_right.get_text())
                self.label_view_name_penalty_player_1_right.set_text(self.entry_name_penalty_player_1_left.get_text())
                self.label_view_name_penalty_player_2_right.set_text(self.entry_name_penalty_player_2_left.get_text())
                self.label_view_name_penalty_player_3_right.set_text(self.entry_name_penalty_player_3_left.get_text())
            else:
                self.label_view_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_left.get_text())
                self.label_view_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_left.get_text())
                self.label_view_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_left.get_text())
                self.label_view_name_penalty_player_1_right.set_text(self.entry_name_penalty_player_1_right.get_text())
                self.label_view_name_penalty_player_2_right.set_text(self.entry_name_penalty_player_2_right.get_text())
                self.label_view_name_penalty_player_3_right.set_text(self.entry_name_penalty_player_3_right.get_text())

            if left_team_is_blue:  # left team is blue in the control view

                self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                             gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 1, 1))
                self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

                self.label_control_team_name_left.set_text(self.entry_team_blue_name.get_text())
                self.label_control_team_name_right.set_text(self.entry_team_white_name.get_text())

                self.label_view_team_name_left.set_text(self.entry_team_blue_name.get_text())
                self.label_view_team_name_right.set_text(self.entry_team_white_name.get_text())

                self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

            else:

                self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                             gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(0, 0, 1, 1))
                self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

                self.label_control_team_name_left.set_text(self.entry_team_white_name.get_text())
                self.label_control_team_name_right.set_text(self.entry_team_blue_name.get_text())

                self.label_view_team_name_left.set_text(self.entry_team_white_name.get_text())
                self.label_view_team_name_right.set_text(self.entry_team_blue_name.get_text())

                self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

    def inverted_view(self, widget, data=None):
        if self.button_separate_game_view_on.get_active():
            #print("********************************")
            #print("**                            **")
            #print("**  inverted view window on   **")
            #print("**                            **")
            #print("********************************")

            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_right.get_text())
                self.label_view_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_right.get_text())
                self.label_view_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_right.get_text())
                self.label_view_name_penalty_player_1_right.set_text(self.entry_name_penalty_player_1_left.get_text())
                self.label_view_name_penalty_player_2_right.set_text(self.entry_name_penalty_player_2_left.get_text())
                self.label_view_name_penalty_player_3_right.set_text(self.entry_name_penalty_player_3_left.get_text())
            else:
                self.label_view_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_left.get_text())
                self.label_view_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_left.get_text())
                self.label_view_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_left.get_text())
                self.label_view_name_penalty_player_1_right.set_text(self.entry_name_penalty_player_1_right.get_text())
                self.label_view_name_penalty_player_2_right.set_text(self.entry_name_penalty_player_2_right.get_text())
                self.label_view_name_penalty_player_3_right.set_text(self.entry_name_penalty_player_3_right.get_text())


            if left_team_is_blue:  # left team is blue in the control view
                self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                             gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(1, 1, 1, 1))
                self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                self.label_control_team_name_left.set_text(self.entry_team_blue_name.get_text())
                self.label_control_team_name_right.set_text(self.entry_team_white_name.get_text())

                self.label_view_team_name_right.set_text(self.entry_team_blue_name.get_text())
                self.label_view_team_name_left.set_text(self.entry_team_white_name.get_text())

                self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

            else:
                self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                             gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 1, 1))
                self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(1, 1, 1, 1))
                self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                self.label_control_team_name_left.set_text(self.entry_team_white_name.get_text())
                self.label_control_team_name_right.set_text(self.entry_team_blue_name.get_text())

                self.label_view_team_name_right.set_text(self.entry_team_white_name.get_text())
                self.label_view_team_name_left.set_text(self.entry_team_blue_name.get_text())

                self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))


    def exit_view_window(self, widget, data=None):
        self.viewwindow.hide()
        self.button_separate_game_view_off.set_active(True)

    def cancel_logdialog(self, widget, data=None):
        #print("**************************")
        #print("**                      **")
        #print("**  cancel log window   **")
        #print("**                      **")
        #print("**************************")
        self.logcanceldialog.show()

    def logcancel_confirmed(self, widget, data=None):
        global logfile_game
        self.logdialog.hide()
        self.penaltylogdialog.hide()
        self.logcanceldialog.hide()
        logfile_game_handler = open(logfile_game, 'a')
        now = datetime.now()
        logfile_game_handler.write("************* control board activity **************\n")
        logfile_game_handler.write("logging data entry window cancelled\n")
        logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
        logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))
        logfile_game_handler.write("***************************************************\n")
        logfile_game_handler.close()

    def logcancel_aborted(self, widget, data=None):
        self.logcanceldialog.hide()

    def reset_confirmed(self, widget, data=None):
        global logfile_game
        global running_first_period_time, running_second_period_time, break_mode, penalty_mode, timeout_mode
        global buffer_last_started_ellapsed_period_time_seconds
        global stopped_special_time_sequence
        global ellapsed_period_time_seconds
        global counter_seconds_board
        global counter_seconds_special_time_sequence
        global game_started
        global action_start_time_of_the_game_is_ACTIVE
        global logfile_game_handler
        '''all timers will be resetted; this can be done for a new game'''
        #
        self.resetdialog.hide()

        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            now = datetime.now()
            logfile_game_handler.write("************* control board activity **************\n")
            logfile_game_handler.write("reset of all timers\n  at time: %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                       "reset of all timers\n  at time: %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()

        #print("button overall time reset pushed")
        # resest functionality
        #
        # re start
        #
        # thread_time_control.cancelled = True?

        if thread_time_control.is_alive():
            #print("*******************************************************")
            #print("**                                                   **")
            #print("**  thread time control alive -> reset will be done  **")
            #print("**                                                   **")
            #print("*******************************************************")
            running_first_period_time = False
            running_second_period_time = False
            game_started=False
            self.button_stop_watch.set_active(True)
            counter_seconds_board = 60 * int(self.spinbutton_period_time.get_value())
            self.togglebutton_start_stop_game.set_active(False)
            action_start_time_of_the_game_is_ACTIVE = False
            # put the label status in order to announce the next possible action is to "start"
            #
            break_mode = False
            penalty_mode = False
            timeout_mode = False
            buffer_label_to_appear = "none"
            self.label_view_specific_timesequence.set_text(buffer_label_to_appear)
            self.label_view_status_specific_timesequence.set_text(buffer_label_to_appear)
            self.label_view_special_time_sequence.set_text(buffer_label_to_appear)
            buffer_last_started_ellapsed_period_time_seconds = 0
            stopped_special_time_sequence = True
            ellapsed_period_time_seconds = 0
            counter_seconds_special_time_sequence = 0
            action_start_time_of_the_game_is_ACTIVE = False
            # clear all timepenalty here
            self.button_clear_timepenalty_player_1_left.set_active(True)
            self.clear_time_penalty_entry_player_1_left(self)
            self.button_clear_timepenalty_player_2_left.set_active(True)
            self.clear_time_penalty_entry_player_2_left(self)
            self.button_clear_timepenalty_player_3_left.set_active(True)
            self.clear_time_penalty_entry_player_3_left(self)
            self.button_clear_timepenalty_player_1_right.set_active(True)
            self.clear_time_penalty_entry_player_1_right(self)
            self.button_clear_timepenalty_player_2_right.set_active(True)
            self.clear_time_penalty_entry_player_2_right(self)
            self.button_clear_timepenalty_player_3_right.set_active(True)
            self.clear_time_penalty_entry_player_3_right(self)


            self.label_control_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                        gdk.RGBA(0, 0, 0, 1))
            self.label_control_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                      gdk.RGBA(0, 0, 0, 1))
            self.label_control_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                      gdk.RGBA(0, 0, 0, 1))

            self.label_control_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                      gdk.RGBA(0, 0, 0, 1))
            self.label_control_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                          gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                       gdk.RGBA(0, 0, 0, 1))
            self.label_control_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                          gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                       gdk.RGBA(0, 0, 0, 1))

            self.label_control_current_time.override_color(gtk.StateFlags.NORMAL,
                                                           gdk.RGBA(0, 0, 0, 1))
            self.label_view_current_time.override_color(gtk.StateFlags.NORMAL,
                                                        gdk.RGBA(0, 0, 0, 1))

            self.togglebutton_start_stop_game.set_label('   START\nPLAY Time')
            self.togglebutton_start_stop_game.set_active(False)
            self.clear_reset_current_time(self)


    def reset_aborted(self, widget, data=None):
        self.resetdialog.hide()
        # reset aborted: nothing will be done hereafter

    def scoreboard_reset_confirm(self, widget, data=None):
        self.resetdialog.show()

    def save_and_exit_logdialog(self, widget, data=None):
        global logfile_game
        global logfile_game_handler
        global logdata_array
        global goal_can_be_increased
        global timeout_can_be_increased
        global timepenalty_can_be_activated
        global penalty_can_be_activated
        global warning_can_be_stored
        '''
        the logdialog will be saved into a logfile. for now, the wide is 11 character too much
        for a good printing with openoffice or leafpad. the comment should be maximum 19 charactier wide; today it
        is 30 character wide. perhaps this should be updated later
        '''

        # initially, all following actions can be done. It will be changed to False if during the data check, anything
        # wrong is found in consistency or log logic or game logic.
        goal_can_be_increased = True
        timeout_can_be_increased = True
        timepenalty_can_be_activated = True
        penalty_can_be_activated = True
        warning_can_be_stored = True

        #print("**********************************")
        #print("**                              **")
        #print("**  save data from log editor   **")
        #print("**                              **")
        #print("**********************************")
        #*************************************************************
        # read the log windows entries
        # test if anything was included in the log window, then store
        #
        for i in range(10):
            for j in range(14):
                if j==0:
                    if self.entry_logarray[i][j].get_active():
                        logdata_array[i][j] = "B"
                    else:
                        logdata_array[i][j] = "_"
                elif j==1:
                    if self.entry_logarray[i][j].get_active():
                        logdata_array[i][j] = "W"
                    else:
                        logdata_array[i][j] = "_"

                elif j==2 or j==13:
                    logdata_array[i][j] = self.entry_logarray[i][j].get_text()

                else:
                    if self.entry_logarray[i][j].get_active():
                        logdata_array[i][j] = "yes"
                    else:
                        logdata_array[i][j] = "_"


        #*************************************************************
        logfile_game_handler = open(logfile_game, 'a')
        logfile_game_handler.write("************************************************************************************************************************************\n")
        logfile_game_handler.write("*  detailled log                                                                                                                   *\n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                    "*  detailled log                                                                                                                   *\n")

        logfile_game_handler.write("************************************************************************************************************************************\n")
#        logfile_game_handler.write("at countdown: %s\n" % (self.label_log_dialog_time.get_text()))
        logfile_game_handler.write('{} {}\n'.format('at countdown:', self.label_log_dialog_time.get_text()))

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              '{} {}\n'.format('at countdown:', self.label_log_dialog_time.get_text()))

        logfile_game_handler.write("                                                 |\n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "                                                 |\n")

        logfile_game_handler.write("event ->                                         | next start will be -> \n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "event ->                                         | next start will be -> \n")

        logfile_game_handler.write("col | nb | warning | time    | player   | player | timeout | free | referee | team | penalty | goal | comment \n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "col | nb | warning | time    | player   | player | timeout | free | referee | team | penalty | goal | comment \n")

        logfile_game_handler.write("    |    |         | penalty | ejection | change |         |      | ball    | ball |         |      |  \n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "    |    |         | penalty | ejection | change |         |      | ball    | ball |         |      |  \n")

        logfile_game_handler.write("    |    |         |         |          |        |         |      |         |      |         |      |  \n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "    |    |         |         |          |        |         |      |         |      |         |      |  \n")

        #                           1_1x|x11x|x111xxxxx|x111xxxxx|x111xxxxxx|x111xxxx|x111xxxxx|x111xx|x111xxxxx|x111xx|x111xxxxx|x111xx|x30x
        # will write log data only if a line was not empty
        for i in range(10):
            line_intact = True
            for j in range(14):
                if logdata_array[i][j] != "_" and logdata_array[i][j] != "":
                    line_intact = False
                if j==13 and not line_intact:
                    logfile_game_handler.write('{:1}_{:1} | {:_<2} | {:_<3}____ | {:_<3}____ | {:_<3}_____ | {:_<3}___ | {:_<3}____ | {:_<3}_ | {:_<3}____ | {:_<3}_ | {:_<3}____ | {:_<3}_ | {:<30}\n'.format(logdata_array[i][0], logdata_array[i][1], logdata_array[i][2], logdata_array[i][3],logdata_array[i][4], logdata_array[i][5], logdata_array[i][6], logdata_array[i][7],logdata_array[i][8], logdata_array[i][9], logdata_array[i][10], logdata_array[i][11],logdata_array[i][12], logdata_array[i][13]))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            '{:1}_{:1} | {:_<2} | {:_<3}____ | {:_<3}____ | {:_<3}_____ | {:_<3}___ | {:_<3}____ | {:_<3}_ | {:_<3}____ | {:_<3}_ | {:_<3}____ | {:_<3}_ | {:<30}\n'.format(logdata_array[i][0], logdata_array[i][1], logdata_array[i][2], logdata_array[i][3],logdata_array[i][4], logdata_array[i][5], logdata_array[i][6], logdata_array[i][7],logdata_array[i][8], logdata_array[i][9], logdata_array[i][10], logdata_array[i][11],logdata_array[i][12], logdata_array[i][13]))

                    #logfile_game_handler.write("%1s_%1s | %2s | %3s     | %3s     | %3s      | %3s    | %3s     | %3s  | %3s     | %3s  | %3s     | %3s  | %-30s\n" %(logdata_array[i][0],logdata_array[i][1],logdata_array[i][2],logdata_array[i][3],logdata_array[i][4],logdata_array[i][5],logdata_array[i][6],logdata_array[i][7],logdata_array[i][8],logdata_array[i][9],logdata_array[i][10],logdata_array[i][11],logdata_array[i][12],logdata_array[i][13]))
        logfile_game_handler.write("remark referee :  %-s\n" % (self.entry_log_dialog_remark_referee.get_text()))

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "remark referee :  %-s\n" % (self.entry_log_dialog_remark_referee.get_text()))

        logfile_game_handler.write("remark scripter:  %-s\n" % (self.entry_log_dialog_remark_scripter.get_text()))

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "remark scripter:  %-s\n" % (self.entry_log_dialog_remark_scripter.get_text()))

        logfile_game_handler.write("************************************************************************************************************************************\n")
        logfile_game_handler.close()

        self.checklogdata(self,"all")
        self.transferlog_to_board(self)

        self.logdialog.hide()

        ####################################
        # clean the log window entries before the window opens again
        #
        for i in range(10):
            for j in range(14):
                if j == 0:
                    self.entry_logarray[i][j].set_active(False)
                elif j == 1:
                    self.entry_logarray[i][j].set_active(False)
                elif j == 2 or j == 13:
                    self.entry_logarray[i][j].set_text("")
                else:
                    self.entry_logarray[i][j].set_active(False)

        self.entry_log_dialog_remark_referee.set_text("")
        self.entry_log_dialog_remark_scripter.set_text("")
        self.label_log_dialog_message.set_text("")
        ####################################

    def checklogdata(self, widget, *data):
        global logdata_array
        global goal_can_be_increased
        global timeout_can_be_increased
        global timepenalty_can_be_activated
        global penalty_can_be_activated
        global warning_can_be_stored
        global penalty_can_be_activated_from_logdata
        global penalty_color_from_logdata
        global finally_identified_penalty_color_from_logdata

        '''logic for checking the entries
        1.  set ok if goal can go up later (all conditions fulfilled)
        2.  set ok if timeout can go up later (all conditions ffulfilled)
        3.  set ok if timepenalty can be activated later
        4.  second warning of a player: info message him to go to timepenalty
        5.  same line: B and W not clicked together
        6.  same player: no ejection and exchange together
        8.  same player: no ejection and timepenalty together
        9.  penalty / goal / free / teamball / referee ball, never together
        11. timepenalty and no W and no B and no nb: warning message
        12. warning and no B and no W and no nb given: warnmessage
        13. penalty: W or B must be given Error message
        14. free: W or B should be given Warnmessage
        15. player ejection: B or W and Nb must be given
        16. player change: warning B or W to be given (and indicate number)
        17. goal and no B and no W; additional info the Nb should be defined
        18. timeout clicked: warning message if no B and no W choosen
        19. player ejection and change not on the same line
        20. player ejection and timepenalty not on the same line
        21. same column: not > 1x free goal penalty teamball refereeball
        22. same player: not > 2x timepenalty
        23. same team 2x timeout
        24. 2x time warning same player
        25. timeout already at 1 and cannot be increased
        26. B or W clicked for timeout timepenalty goal warning penalty free player ejec/change 
        27. teamball or refereeball released, check the line if number player missing
        28. when goal of other team and a player in timepenalty, release him
        '''
        #checkparam = data[1]
        #print("**  start checklogdata   **")
        #print("data", data)
        checkparam = data[0]
        #print("checkparam",checkparam)

        # check1: result at the end
        goal_can_be_increased = True

        # check2: result at the end
        timeout_can_be_increased = True

        # ckeck3; result at the end
        timepenalty_can_be_activated = True

        penalty_can_be_activated = True

        warning_can_be_stored = True

        checkarea = [0,0] # default: no search when nothing activated
        checkfokus = [0,0] # default: no search

        self.label_log_dialog_message.set_text("")
        textmessage = ""

        penalty_can_be_activated_from_logdata = True
        penalty_color_from_logdata = None

        #*************************************************************
        # read the log windows entries
        # test if anything was included in the log window, then store
        #
        for i in range(10):
            for j in range(14):
                if j==0:
                    if self.entry_logarray[i][j].get_active():
                        logdata_array[i][j] = "B"

                        if i > checkarea[0]:
                            checkarea[0] = i
                        if j > checkarea[1]:
                            checkarea[1] = j

                    else:
                        logdata_array[i][j] = "_"
                elif j==1:
                    if self.entry_logarray[i][j].get_active():
                        logdata_array[i][j] = "W"

                        if i > checkarea[0]:
                            checkarea[0] = i
                        if j > checkarea[1]:
                            checkarea[1] = j

                    else:
                        logdata_array[i][j] = "_"

                elif j==2 or j==13:
                    logdata_array[i][j] = self.entry_logarray[i][j].get_text()

                else:
                    if self.entry_logarray[i][j].get_active():
                        logdata_array[i][j] = "yes"

                        if i > checkarea[0]:
                            checkarea[0] = i
                        if j > checkarea[1]:
                            checkarea[1] = j

                    else:
                        logdata_array[i][j] = "_"

        #print("checkarea", checkarea)

        if checkparam== "all":
            checkfokus[0] = 9 # i line
            checkfokus[1] =13 # j column
        else:
            checkfokus[0] = int(checkparam[2:4]) # "lpxx_yy"
            checkfokus[1] = int(checkparam[5:7])

        print("checkfokus in main log window ", checkfokus[0],checkfokus[1])
        print("checkarea in main log window",checkarea[0], checkarea[1])

        #print("check 4")
        #check4
        #for i in range(10):
        if checkfokus[1] == 3 and checkfokus[0] <= checkarea[0]:
            for i in range(checkarea[0]+1):
                if logdata_array[i][3] == "yes" and logdata_array[i][2] != "":
                    # check if already in warning list
                    self.label_log_dialog_message.set_text("I: check if already in warning list\n   then give timepalty")
                    #time.sleep(0.2)

        # check 5
        if (checkfokus[1] == 0 or checkfokus[1] == 1) and checkfokus[0] <= checkarea[0]:
            print("check 5 main log window")
            for i in range(checkarea[0]+1):
                if logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    self.label_log_dialog_message.set_text("E: B and W not on the same line")
                    #if logdata_array[i][11] == "yes":
                        #penalty_can_be_activated_from_logdata = False
                        #penalty_color_from_logdata = ""
                elif (logdata_array[i][0] == "_" and logdata_array[i][1] == "_") and logdata_array[i][11] == "yes":
                    penalty_color_from_logdata = ""
                    self.label_log_dialog_message.set_text("W: B or W to be choosen for penalty")
                elif (logdata_array[i][0] == "B" or logdata_array[i][1] == "W") and logdata_array[i][11] == "yes":
                    penalty_color_from_logdata = logdata_array[i][0]
                    if penalty_color_from_logdata=="_":
                        penalty_color_from_logdata=logdata_array[i][1]
                else:
                    pass
                print("penalty_color_from_logdata ",penalty_color_from_logdata)

        #print("check 6")
        # check 6
        if (checkfokus[1] == 5 or checkfokus[1] == 6) and checkfokus[0] <= checkarea[0]:
            for i in range(checkarea[0]+1):
                if logdata_array[i][5] == "yes":   # player ejection detected; detect now if the same player is changed
                    for j in range(checkarea[0]+1):
                        if logdata_array[j][6] == "yes":  # detect now if the same player is changed = nb in comment
                            if self.entry_logarray[j][13].get_text().find(self.entry_logarray[i][2].get_text()) != -1:
                                self.label_log_dialog_message.set_text("E: player ejection and change not for same number")
                                #time.sleep(0.2)
        #print("check 8")
        # check 8
        if (checkfokus[1] == 5 or checkfokus[1] == 4) and checkfokus[0] <= checkarea[0]:
            for i in range(checkarea[0]+1):
                if logdata_array[i][5] == "yes":   # player ejection detected; detect now if the same player is timepenalty
                    for j in range(checkarea[0]+1):
                        if logdata_array[j][4] == "yes":  # detect now if the same player is changed = nb in comment
                            if self.entry_logarray[j][2].get_text() == self.entry_logarray[i][2].get_text():
                                self.label_log_dialog_message.set_text("E: player ejection and timepenalty not for same number")
                                #time.sleep(0.2)
        #print("check 11")
        #check11
        for i in range(checkarea[0]+1):
            textmessage = ""

            if logdata_array[i][4] == "yes" and logdata_array[i][0] == "_" and \
                    logdata_array[i][1] == "_":
                textmessage = "E: choose B or W for timepenalty"
                timepenalty_can_be_activated = False

            if logdata_array[i][4] == "yes" and logdata_array[i][0] == "B" and \
                    logdata_array[i][1] == "W":
                textmessage = "E: B and W cannot be choosen together for timepenalty"
                timepenalty_can_be_activated = False

            if logdata_array[i][4] == "yes" and logdata_array[i][2] == "":
                textmessage = textmessage + "\nE: choose nb for timepenalty"
                timepenalty_can_be_activated = False

            self.label_log_dialog_message.set_text(textmessage)

        #print("check 12")
        # check12
        if checkfokus[1] == 3 and checkfokus[0] <= checkarea[0]:
            textmessage = ""

            if logdata_array[i][3] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                textmessage = "E: choose B or W for player warning"

            if logdata_array[i][3] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                textmessage = "E: B and W cannot be choosen together for player warning"

            if logdata_array[i][3] == "yes" and logdata_array[i][2] == "":
                textmessage = textmessage + "\nW: choose nb for player warning"

            self.label_log_dialog_message.set_text(textmessage)

        #check13
        if checkfokus[1] == 11 and checkfokus[0] <= checkarea[0]:
            print("check 13 in main log window")
            if logdata_array[checkfokus[0]][11] == "yes" and logdata_array[checkfokus[0]][0] == "_" and logdata_array[checkfokus[0]][1] == "_":
                self.label_log_dialog_message.set_text("W: choose B or W for penalty")
                penalty_color_from_logdata = ""
                #penalty_can_be_activated_from_logdata = False

            elif logdata_array[checkfokus[0]][11] == "yes" and logdata_array[checkfokus[0]][0] == "B" and logdata_array[checkfokus[0]][1] == "W":
                self.label_log_dialog_message.set_text("W: B and W cannot be choosen together for penalty")
                #penalty_can_be_activated_from_logdata = False
                penalty_color_from_logdata = ""

            elif (logdata_array[checkfokus[0]][0] == "B" or logdata_array[checkfokus[0]][1] == "W") and logdata_array[checkfokus[0]][11] == "yes":
                penalty_color_from_logdata = logdata_array[checkfokus[0]][0]
                if penalty_color_from_logdata == "_":
                    penalty_color_from_logdata = logdata_array[checkfokus[0]][1]

            else:
                pass
            print("penalty_color_from_logdata ", penalty_color_from_logdata)

        #print("check 14")
        #check14
        if checkfokus[1] == 8 and checkfokus[0] <= checkarea[0]:
            if logdata_array[checkfokus[0]][8] == "yes" and logdata_array[checkfokus[0]][0] == "_" and logdata_array[checkfokus[0]][1] == "_":
                self.label_log_dialog_message.set_text("W: choose B or W (against) for a free")
                #time.sleep(0.2)
            if logdata_array[checkfokus[0]][8] == "yes" and logdata_array[checkfokus[0]][0] == "B" and logdata_array[checkfokus[0]][1] == "W":
                self.label_log_dialog_message.set_text("W: B and W cannot be choosen together for a free")
                #time.sleep(0.2)

        #print("check 15")
        #check15
        if checkfokus[1] == 5 and checkfokus[0] <= checkarea[0]:
            #if checkparam == "all":
            for i in range(checkarea[0]+1):

                textmessage = ""

                if logdata_array[i][5] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                    textmessage = "E: choose B or W for player ejection"

                if logdata_array[i][5] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    textmessage = "E: B and W cannot be choosen together for player ejection"

                if logdata_array[i][5] == "yes" and logdata_array[i][2] == "":
                    textmessage = textmessage + "\nE: choose nb for player ejection"

                self.label_log_dialog_message.set_text(textmessage)


        #print("check 16")
        # check16
        if checkfokus[1] == 6 and checkfokus[0] <= checkarea[0]:
            #if checkparam == "all":
            for i in range(checkarea[0]+1):

                textmessage = ""

                if logdata_array[i][6] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                    textmessage = "W: choose B or W for player change"


                if logdata_array[i][6] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    textmessage = "E: B and W cannot be choosen together for player change"

                if logdata_array[i][6] == "yes" and logdata_array[i][2] == "":
                    textmessage = textmessage + "\nW: choose nb for player going out left\nput new player number coming-in right comment "

                self.label_log_dialog_message.set_text(textmessage)

        #print("check 17")
        # check17
        if checkfokus[1] == 12 and checkfokus[0] <= checkarea[0]:
            #if checkparam == "all":
            for i in range(checkarea[0]+1):
                if logdata_array[i][12] == "yes":
                    textmessage = ""

                    if logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                        textmessage = "E: cannot choose B and W for goal"
                        goal_can_be_increased = False

                    if logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                        textmessage = "E: choose B or W for goal"
                        goal_can_be_increased = False

                    if logdata_array[i][2] == "":
                        textmessage = textmessage + "\nI: put nb of the player having scored"

                    self.label_log_dialog_message.set_text(textmessage)

        #print("check 18")
        #check18
        for i in range(checkarea[0]+1):
            if logdata_array[i][7] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                self.label_log_dialog_message.set_text("E: choose B or W for timeout")
                timeout_can_be_increased = False
                #time.sleep(0.2)
        #print("check 19")
        # check 19
        for i in range(checkarea[0]+1):
            if logdata_array[i][5] == "yes" and logdata_array[i][6] == "yes":
                self.label_log_dialog_message.set_text("w: player ejection and change not on the same line")
                #time.sleep(0.2)
        #print("check 20")
        # check 20
        for i in range(checkarea[0]+1):
            if logdata_array[i][4] == "yes" and logdata_array[i][5] == "yes":
                self.label_log_dialog_message.set_text("w: player ejection and timepenalty not on the same line")
                #time.sleep(0.2)
        #print("check 21")
        # check 21
        event_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][8] == "yes":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not 2 times free")
                #time.sleep(0.2)

        event_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][9] == "yes":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not 2 times referee ball")
                #time.sleep(0.2)

        event_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][10] == "yes":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not 2 times team ball")
                #time.sleep(0.2)

        event_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][11] == "yes":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not 2 times penalty")
                    penalty_can_be_activated = False
                #time.sleep(0.2)

        event_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][12] == "yes":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not 2 times goal")
                    goal_can_be_increased = False
                #time.sleep(0.2)
        #print("check 22")
        #check 22

        #print("check 9")
        # check 9
        event_detected = False

        freeevent_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][8] == "yes" and not freeevent_detected:
                freeevent_detected = True
                event_detected = True

        refereeballevent_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][9] == "yes" and not refereeballevent_detected:
                refereeballevent_detected = True
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not same time free / referee ball / team ball / penalty / goal")
                        #time.sleep(0.2)

        teamballevent_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][10] == "yes" and not teamballevent_detected:
                teamballevent_detected = True
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not same time free / referee ball / team ball / penalty / goal")
                        #time.sleep(0.2)

        penaltyevent_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][11] == "yes" and not penaltyevent_detected:
                penaltyevent_detected = True
                if not event_detected:
                    event_detected = True
                else:
                    timeout_can_be_increased = False # penalty seen but not correctly setup
                    self.label_log_dialog_message.set_text(
                            "E: not same time free / referee ball / team ball / penalty / goal")
                        #time.sleep(0.2)

        goalevent_detected = False
        for i in range(checkarea[0]+1):
            if logdata_array[i][12] == "yes" and not goalevent_detected:
                goalevent_detected = True
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text(
                            "E: not same time free / referee ball / team ball / penalty / goal")
                        #time.sleep(0.2)

        #check 23

        event_detected = False
        for i in range(checkarea[0] + 1):
            if logdata_array[i][7] == "yes" and logdata_array[i][0] == "B":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not 2 times timeout team blue")
                    timeout_can_be_increased = False

        event_detected = False
        for i in range(checkarea[0] + 1):
            if logdata_array[i][7] == "yes" and logdata_array[i][1] == "W":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_log_dialog_message.set_text("E: not 2 times timeout team white")
                    timeout_can_be_increased = False

        #print("check 24")
        # check24

        # check25
        #print("check 25")
        for i in range(checkarea[0]+1):
            if logdata_array[i][7] == "yes":

                if logdata_array[i][0] == "B":
                    if left_team_is_blue and self.spinbutton_timeout_left.get_value()==1:
                        self.label_log_dialog_message.set_text(
                                "E: no additional timeout possible for team blue")
                        timeout_can_be_increased = False
                    if not left_team_is_blue and self.spinbutton_timeout_right.get_value()==1:
                        self.label_log_dialog_message.set_text(
                                "E: no additional timeout possible for team blue")
                        timeout_can_be_increased = False

                if logdata_array[i][1] == "W":
                    if left_team_is_blue and self.spinbutton_timeout_right.get_value() == 1:
                        self.label_log_dialog_message.set_text(
                                "E: no additional timeout possible for team white")
                        timeout_can_be_increased = False
                    if not left_team_is_blue and self.spinbutton_timeout_left.get_value() == 1:
                        self.label_log_dialog_message.set_text(
                                "E: no additional timeout possible for team white")
                        timeout_can_be_increased = False

        #print("check 26")
        # check26
        if (checkfokus[1] == 0 or checkfokus[1] == 1) and checkfokus[0] <= checkarea[0]:
            # if checkparam == "all":
            for i in range(checkarea[0] + 1):
                if logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    self.label_log_dialog_message.set_text("w: not B and W on the same line")
                elif logdata_array[i][0] != "B" and logdata_array[i][1] != "W":

                    if logdata_array[i][7] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W of the team having timeout")
                        timeout_can_be_increased = False
                        time.sleep(0.1)

                    if logdata_array[i][4] == "yes":
                        self.label_log_dialog_message.set_text("E: choose B or W for timepenalty")
                        time.sleep(0.1)
                        if logdata_array[i][2] == "":
                            self.label_log_dialog_message.set_text("E: choose nb for timepemalty")
                            time.sleep(0.1)

                    if logdata_array[i][12] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W for goal")
                        goal_can_be_increased = False
                        time.sleep(0.1)

                    if logdata_array[i][3] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W for warning")
                        time.sleep(0.1)
                        if logdata_array[i][2] == "":
                            self.label_log_dialog_message.set_text("E: choose nb for warning")
                            time.sleep(0.1)

                    if logdata_array[i][11] == "yes":
                        self.label_log_dialog_message.set_text("E: choose B or W for penalty")
                        time.sleep(0.1)

                    if logdata_array[i][8] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W for free")
                        goal_can_be_increased = False
                        time.sleep(0.1)

                    if logdata_array[i][5] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W for player ejection")
                        time.sleep(0.2)
                        if logdata_array[i][2] == "":
                            self.label_log_dialog_message.set_text("E: choose nb for player ejection")
                            time.sleep(0.1)

                    if logdata_array[i][6] == "yes":
                        self.label_log_dialog_message.set_text("E: choose B or W for player change")

                elif logdata_array[i][0] != "B" or logdata_array[i][1] != "W":

                    if logdata_array[i][4] == "yes" and logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("E: choose nb for timepemalty")
                        time.sleep(0.1)

                    if logdata_array[i][3] == "yes" and logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("E: choose nb for warning")
                        time.sleep(0.1)

                    if logdata_array[i][5] == "yes" and logdata_array[i][2] == "":
                            self.label_log_dialog_message.set_text("E: choose nb for player ejection")
                            time.sleep(0.1)

                    if logdata_array[i][12] == "yes" and logdata_array[i][2] == "":
                            self.label_log_dialog_message.set_text("I: choose nb for goal")
                            time.sleep(0.1)

        #print("check 27")
        # check27
        if checkfokus[0] <= checkarea[0]:

            for i in range(checkarea[0] + 1):

                if logdata_array[i][12] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("I: choose nb player for goal")

                if logdata_array[i][3] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("W: choose nb player for warning")

                if logdata_array[i][5] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("E: choose nb for player ejection")

                if logdata_array[i][4] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("E: choose nb for timepemalty")



        if checkparam == "all":

            event_detected = False
            freeevent_detected = False
            refereeballevent_detected = False
            teamballevent_detected = False
            penaltyevent_detected = False
            goalevent_detected = False

            for i in range(checkarea[0] + 1):

                print("check all in main log window")
                print("penalty_color_from_logdata in check all main log win ", penalty_color_from_logdata)

                if logdata_array[i][11] == "yes" and logdata_array[i][0] == "_" and \
                        logdata_array[i][1] == "_":
                    self.label_log_dialog_message.set_text("W: choose B or W for penalty")
                    penalty_color_from_logdata = ""
                    # penalty_can_be_activated_from_logdata = False

                elif logdata_array[i][11] == "yes" and logdata_array[i][0] == "B" and \
                        logdata_array[i][1] == "W":
                    self.label_log_dialog_message.set_text("W: B and W cannot be choosen together for penalty")
                    # penalty_can_be_activated_from_logdata = False
                    penalty_color_from_logdata = ""

                elif (logdata_array[i][0] == "B" or logdata_array[i][1] == "W") and \
                        logdata_array[i][11] == "yes":
                    penalty_color_from_logdata = logdata_array[i][0]
                    if penalty_color_from_logdata == "_":
                        penalty_color_from_logdata = logdata_array[i][1]

                        for i in range(checkarea[0] + 1):
                            if logdata_array[i][3] == "yes" and logdata_array[i][2] != "":
                                # check if already in warning list
                                self.label_log_dialog_message.set_text(
                                    "I: check if already in warning list\n   then give timepalty")


                # print("check 6")
                # check 6
                if logdata_array[i][5] == "yes":  # player ejection detected; detect now if the same player is changed
                    for j in range(checkarea[0] + 1):
                        if logdata_array[j][6] == "yes":  # detect now if the same player is changed = nb in comment
                            if self.entry_logarray[j][13].get_text().find(
                                self.entry_logarray[i][2].get_text()) != -1:
                                self.label_log_dialog_message.set_text("E: player ejection and change not for same number")
                                # time.sleep(0.2)
                # print("check 8")
                # check 8
                if logdata_array[i][5] == "yes":  # player ejection detected; detect now if the same player is timepenalty
                    for j in range(checkarea[0] + 1):
                        if logdata_array[j][4] == "yes":  # detect now if the same player is changed = nb in comment
                            if self.entry_logarray[j][2].get_text() == self.entry_logarray[i][2].get_text():
                                self.label_log_dialog_message.set_text("E: player ejection and timepenalty not for same number")
                                # time.sleep(0.2)
                    # print("check 11")
                    # check11
                textmessage = ""

                if logdata_array[i][4] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                    textmessage = "E: choose B or W for timepenalty"
                    timepenalty_can_be_activated = False

                if logdata_array[i][4] == "yes" and logdata_array[i][0] == "B" and \
                                logdata_array[i][1] == "W":
                    textmessage = "E: B and W cannot be choosen together for timepenalty"
                    timepenalty_can_be_activated = False

                if logdata_array[i][4] == "yes" and logdata_array[i][2] == "":
                    textmessage = textmessage + "\nE: choose nb for timepenalty"
                    timepenalty_can_be_activated = False

                self.label_log_dialog_message.set_text(textmessage)

                # print("check 12")
                # check12
                textmessage = ""

                if logdata_array[i][3] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                    textmessage = "E: choose B or W for player warning"

                if logdata_array[i][3] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    textmessage = "E: B and W cannot be choosen together for player warning"

                if logdata_array[i][3] == "yes" and logdata_array[i][2] == "":
                    textmessage = textmessage + "\nW: choose nb for player warning"

                self.label_log_dialog_message.set_text(textmessage)

                # print("check 14")
                # check14
                if logdata_array[i][8] == "yes" and logdata_array[i][0] == "_" and \
                                logdata_array[checkfokus[0]][1] == "_":
                    self.label_log_dialog_message.set_text("W: choose B or W (against) for a free")
                            # time.sleep(0.2)
                if logdata_array[i][8] == "yes" and logdata_array[i][0] == "B" and \
                                logdata_array[i][1] == "W":
                    self.label_log_dialog_message.set_text("W: B and W cannot be choosen together for a free")
                            # time.sleep(0.2)

                # print("check 15")
                # check15
                textmessage = ""

                if logdata_array[i][5] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][
                                1] == "_":
                    textmessage = "E: choose B or W for player ejection"

                if logdata_array[i][5] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][
                                1] == "W":
                    textmessage = "E: B and W cannot be choosen together for player ejection"

                if logdata_array[i][5] == "yes" and logdata_array[i][2] == "":
                    textmessage = textmessage + "\nE: choose nb for player ejection"

                    self.label_log_dialog_message.set_text(textmessage)

                    # print("check 16")
                    # check16
                textmessage = ""

                if logdata_array[i][6] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][
                                1] == "_":
                    textmessage = "W: choose B or W for player change"

                if logdata_array[i][6] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][
                                1] == "W":
                    textmessage = "E: B and W cannot be choosen together for player change"

                if logdata_array[i][6] == "yes" and logdata_array[i][2] == "":
                                textmessage = textmessage + "\nW: choose nb for player going out left\nput new player number coming-in right comment "

                self.label_log_dialog_message.set_text(textmessage)

                # print("check 17")
                # check17
                if logdata_array[i][12] == "yes":
                    textmessage = ""

                    if logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                        textmessage = "E: cannot choose B and W for goal"
                        goal_can_be_increased = False

                    if logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                        textmessage = "E: choose B or W for goal"
                        goal_can_be_increased = False

                    if logdata_array[i][2] == "":
                        textmessage = textmessage + "\nI: put nb of the player having scored"
                    self.label_log_dialog_message.set_text(textmessage)

                # print("check 18")
                # check18
                if logdata_array[i][7] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                    self.label_log_dialog_message.set_text("E: choose B or W for timeout")
                    timeout_can_be_increased = False

                # print("check 19")
                # check 19
                if logdata_array[i][5] == "yes" and logdata_array[i][6] == "yes":
                     self.label_log_dialog_message.set_text("w: player ejection and change not on the same line")

                # print("check 20")
                # check 20
                if logdata_array[i][4] == "yes" and logdata_array[i][5] == "yes":
                    self.label_log_dialog_message.set_text(
                                "w: player ejection and timepenalty not on the same line")

                # print("check 22")
                # check 22

                # print("check 9")
                # check 9


                if logdata_array[i][8] == "yes" and not freeevent_detected:
                    freeevent_detected = True
                    event_detected = True

                if logdata_array[i][9] == "yes" and not refereeballevent_detected:
                    refereeballevent_detected = True
                    if not event_detected:
                        event_detected = True
                    else:
                        self.label_log_dialog_message.set_text(
                        "E: not same time free / referee ball / team ball / penalty / goal")

                if logdata_array[i][10] == "yes" and not teamballevent_detected:
                    teamballevent_detected = True
                    if not event_detected:
                        event_detected = True
                    else:
                        self.label_log_dialog_message.set_text(
                            "E: not same time free / referee ball / team ball / penalty / goal")

                if logdata_array[i][11] == "yes" and not penaltyevent_detected:
                    penaltyevent_detected = True
                    if not event_detected:
                        event_detected = True
                    else:
                        penalty_can_be_activated = False  # penalty seen but not correctly setup
                        self.label_log_dialog_message.set_text(
                                    "E: not same time free / referee ball / team ball / penalty / goal")

                if logdata_array[i][12] == "yes" and not goalevent_detected:
                    goalevent_detected = True
                    if not event_detected:
                        event_detected = True
                    else:
                        goal_can_be_increased = False
                        self.label_log_dialog_message.set_text(
                                    "E: not same time free / referee ball / team ball / penalty / goal")

                # check25
                # print("check 25")
                if logdata_array[i][7] == "yes":

                    if logdata_array[i][0] == "B":
                        if left_team_is_blue and self.spinbutton_timeout_left.get_value() == 1:
                            self.label_log_dialog_message.set_text(
                                        "E: no additional timeout possible for team blue")
                            timeout_can_be_increased = False
                        if not left_team_is_blue and self.spinbutton_timeout_right.get_value() == 1:
                            self.label_log_dialog_message.set_text(
                                        "E: no additional timeout possible for team blue")
                            timeout_can_be_increased = False

                    if logdata_array[i][1] == "W":
                        if left_team_is_blue and self.spinbutton_timeout_right.get_value() == 1:
                            self.label_log_dialog_message.set_text(
                                        "E: no additional timeout possible for team white")
                            timeout_can_be_increased = False
                        if not left_team_is_blue and self.spinbutton_timeout_left.get_value() == 1:
                            self.label_log_dialog_message.set_text(
                                        "E: no additional timeout possible for team white")
                            timeout_can_be_increased = False

                # print("check 26")
                # check26
                if logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    self.label_log_dialog_message.set_text("w: not B and W on the same line")
                elif logdata_array[i][0] != "B" and logdata_array[i][1] != "W":

                    if logdata_array[i][7] == "yes":
                        self.label_log_dialog_message.set_text(
                            "W: choose B or W of the team having timeout")
                        timeout_can_be_increased = False

                    if logdata_array[i][4] == "yes":
                        self.label_log_dialog_message.set_text("E: choose B or W for timepenalty")

                    if logdata_array[i][12] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W for goal")
                        goal_can_be_increased = False

                    if logdata_array[i][3] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W for warning")

                    if logdata_array[i][11] == "yes":
                        self.label_log_dialog_message.set_text("E: choose B or W for penalty")

                    if logdata_array[i][8] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W for free")
                        goal_can_be_increased = False

                    if logdata_array[i][5] == "yes":
                        self.label_log_dialog_message.set_text("W: choose B or W for player ejection")

                    if logdata_array[i][6] == "yes":
                        self.label_log_dialog_message.set_text("E: choose B or W for player change")
                else:
                    pass
                    # print("check 27")
                    # check27
                if logdata_array[i][12] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("W: choose nb player for goal")

                if logdata_array[i][3] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("W: choose nb player for warning")

                if logdata_array[i][5] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("E: choose nb for player ejection")

                if logdata_array[i][4] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("E: choose nb for timepemalty")

                if logdata_array[i][6] == "yes":
                    if logdata_array[i][2] == "":
                        self.label_log_dialog_message.set_text("E: choose nb for player change")

            print("penalty_color_from_logdata in main log window after check all", penalty_color_from_logdata)
            finally_identified_penalty_color_from_logdata = penalty_color_from_logdata
        #print("**  end checklogdata   **")


    def transferlog_to_board(self, widget, data=None):
        global goal_can_be_increased
        global timeout_can_be_increased
        global timepenalty_can_be_activated
        global penalty_can_be_activated
        global warning_can_be_stored
        global left_team_is_blue
        global penalty_can_be_activated_from_logdata
        global penalty_color_from_logdata
        global finally_identified_penalty_color_from_logdata
        '''
        1. goal correctly recognized? -> activate it immediatly
        2. penalty correctly recognized? -> activate it and make ready for start
           timeout correctly recognized (no penalty identified) -> activate and start it
        timepenalty correctly recognized? -> activate it and make ready to start
        warning correctly recognized -> store it in the warning list
        '''
        print("begin transferlog to board")
        penalty_can_be_activated_from_logdata =False

        if goal_can_be_increased: # if present...
            for i in range(10):
                if logdata_array[i][12] == "yes":
                    # increase
                    if logdata_array[i][0] == "B":
                        if left_team_is_blue:
                            self.spinbutton_points_team_left.spin(0,1.0)
                        else:
                            self.spinbutton_points_team_right.spin(0,1.0)

                    if logdata_array[i][1] == "W":
                        if left_team_is_blue:
                            self.spinbutton_points_team_right.spin(0,1.0)
                        else:
                            self.spinbutton_points_team_left.spin(0,1.0)

        if penalty_can_be_activated: # if present...
            # activate
            for i in range(10):
                if logdata_array[i][11] == "yes":
                    # activate penalty
                    self.button_special_time_sequence_penalty.set_active(True)
                    penalty_can_be_activated_from_logdata = True
                    penalty_color_from_logdata = logdata_array[i][0]
                    if penalty_color_from_logdata == "_":
                        penalty_color_from_logdata = logdata_array[i][1]
                    print("penalty_color_from_logdata in transferlog ", penalty_color_from_logdata)

                if i==9 and not self.button_special_time_sequence_penalty.get_active():
                    if timeout_can_be_increased: # if present..
                        for j in range(10):
                            if logdata_array[j][7] == "yes":
                                # activate timeout if timeout not already at 1

                                if logdata_array[j][0] == "B":
                                    if left_team_is_blue:
                                        #self.spinbutton_timeout_left.get_value()
                                        self.spinbutton_timeout_left.spin(0, 1.0)
                                    else:
                                        self.spinbutton_timeout_right.spin(0, 1.0)

                                if logdata_array[j][1] == "W":
                                    if left_team_is_blue:
                                        self.spinbutton_timeout_right.spin(0, 1.0)
                                    else:
                                        self.spinbutton_timeout_left.spin(0, 1.0)

                                self.button_special_time_sequence_timeout.set_active(True)
                                self.button_start_special_time_sequence.set_active(True)

        if timepenalty_can_be_activated:

            for i in range(10):
                if logdata_array[i][4] == "yes" and logdata_array[i][2]!="":

                    if left_team_is_blue:

                        if logdata_array[i][0] == "B":

                            if self.entry_name_penalty_player_1_left.get_text()=="":
                                self.entry_name_penalty_player_1_left.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_2_left.get_text()=="":
                                self.entry_name_penalty_player_2_left.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_3_left.get_text()=="":
                                self.entry_name_penalty_player_3_left.set_text(logdata_array[i][2])
                            else:
                                print("scoreboard full, timepenalty cannot be transfered into it")

                        else:
                            if self.entry_name_penalty_player_1_right.get_text()=="":
                                self.entry_name_penalty_player_1_right.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_2_right.get_text()=="":
                                self.entry_name_penalty_player_2_right.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_3_right.get_text()=="":
                                self.entry_name_penalty_player_3_right.set_text(logdata_array[i][2])
                            else:
                                print("scoreboard full, timepenalty cannot be transfered into it")

                    else:

                        if logdata_array[i][0] == "B":
                            if self.entry_name_penalty_player_1_right.get_text()=="":
                                self.entry_name_penalty_player_1_right.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_2_right.get_text()=="":
                                self.entry_name_penalty_player_2_right.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_3_right.get_text()=="":
                                self.entry_name_penalty_player_3_right.set_text(logdata_array[i][2])
                            else:
                                print("scoreboard full, timepenalty cannot be transfered into it")
                        else:
                            if self.entry_name_penalty_player_1_left.get_text()=="":
                                self.entry_name_penalty_player_1_left.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_2_left.get_text()=="":
                                self.entry_name_penalty_player_2_left.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_3_left.get_text()=="":
                                self.entry_name_penalty_player_3_left.set_text(logdata_array[i][2])
                            else:
                                print("scoreboard full, timepenalty cannot be transfered into it")

        if warning_can_be_stored:
            pass

        if timeout_can_be_increased:
            pass

        print("Ende transfer log to board")


    def save_and_exit_penaltylogdialog(self, widget, data=None):
        global logfile_game
        global logfile_game_handler
        global logdata_array
        '''the logdialog will be saved into a logfile. for now, the wide is 11 character too much
        for a good printing with openoffice or leafpad. the comment should be maximum 19 charactier wide; today it
        is 30 character wide. perhaps this should be updated later'''

        for i in range(10):
            for j in range(12):
                if j == 0:
                    if self.entry_penaltylogarray[i][j].get_active():
                        logdata_array[i][j] = "B"
                    else:
                        logdata_array[i][j] = "_"
                elif j == 1:
                    if self.entry_penaltylogarray[i][j].get_active():
                        logdata_array[i][j] = "W"
                    else:
                        logdata_array[i][j] = "_"

                elif j == 2 or j == 11:
                        logdata_array[i][j] = self.entry_penaltylogarray[i][j].get_text()

                else:
                    if self.entry_penaltylogarray[i][j].get_active():
                        logdata_array[i][j] = "yes"
                    else:
                        logdata_array[i][j] = "_"

        # *************************************************************
        logfile_game_handler = open(logfile_game, 'a')
        logfile_game_handler.write(
                "***********************************************************************************************************************\n")
        logfile_game_handler.write(
                "*  detailled log                                                                                                      *\n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                "*  detailled log                                                                                                      *\n")

        logfile_game_handler.write(
                "***********************************************************************************************************************\n")
        logfile_game_handler.write('{} {}\n'.format('at countdown:', self.label_penaltylog_dialog_time.get_text()))

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              '{} {}\n'.format('at countdown:', self.label_penaltylog_dialog_time.get_text()))

        logfile_game_handler.write(
                "                                                           |\n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "                                                           |\n")

        logfile_game_handler.write(
                "event ->                                                   | next start will be -> \n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "event ->                                                   | next start will be -> \n")

        logfile_game_handler.write(
                "col | nb | warning | time    | player   | player | timeout | penalty | penalty | goal | comment \n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "col | nb | warning | time    | player   | player | timeout | penalty | penalty | goal | comment \n")

        logfile_game_handler.write(
                "    |    |         | penalty | ejection | change |         | cancel  |         |      |  \n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "    |    |         | penalty | ejection | change |         | cancel  |         |      |  \n")

        logfile_game_handler.write(
                "    |    |         |         |          |        |         |         |         |      |  \n")

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "    |    |         |         |          |        |         |         |         |      |  \n")

        #        1_1x|x11x|x111xxxxx|x111xxxxx|x111xxxxxx|x111xxxx|x111xxxxx|x111xxxxx|x111xxxxx|x111xx|x30x
            # will write log data only if a line was not empty
        for i in range(10):
            line_intact = True
            for j in range(14):
                if logdata_array[i][j] != "_" and logdata_array[i][j] != "":
                    line_intact = False
                if j == 13 and not line_intact:
                    logfile_game_handler.write(
                            '{:1}_{:1} | {:_<2} | {:_<3}____ | {:_<3}____ | {:_<3}_____ | {:_<3}___ | {:_<3}____ | {:_<3}____ | {:_<3}____ | {:_<3}_ | {:<30}\n'.format(
                            logdata_array[i][0], logdata_array[i][1], logdata_array[i][2], logdata_array[i][3],
                            logdata_array[i][4], logdata_array[i][5], logdata_array[i][6], logdata_array[i][7],
                            logdata_array[i][8], logdata_array[i][9], logdata_array[i][10], logdata_array[i][11]))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          '{:1}_{:1} | {:_<2} | {:_<3}____ | {:_<3}____ | {:_<3}_____ | {:_<3}___ | {:_<3}____ | {:_<3}____ | {:_<3}____ | {:_<3}_ | {:<30}\n'.format(
                            logdata_array[i][0], logdata_array[i][1], logdata_array[i][2], logdata_array[i][3],
                            logdata_array[i][4], logdata_array[i][5], logdata_array[i][6], logdata_array[i][7],
                            logdata_array[i][8], logdata_array[i][9], logdata_array[i][10], logdata_array[i][11]))

        logfile_game_handler.write("remark referee :  %-s\n" % (self.entry_penaltylog_dialog_remark_referee.get_text()))

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "remark referee :  %-s\n" % (self.entry_penaltylog_dialog_remark_referee.get_text()))

        logfile_game_handler.write("remark scripter:  %-s\n" % (self.entry_penaltylog_dialog_remark_scripter.get_text()))

        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                              "remark scripter:  %-s\n" % (self.entry_penaltylog_dialog_remark_scripter.get_text()))

        logfile_game_handler.write(
                "***********************************************************************************************************************\n")
        logfile_game_handler.close()
        self.checkpenaltylogdata(self,"all")
        self.transferpenaltylog_to_board(self)
        self.penaltylogdialog.hide()

        ####################################
        # clean the log window entries before the window opens again
        #
        for i in range(10):
            # desactivate penalty and goal first else W/B could stay activated
            self.entry_penaltylogarray[i][9].set_active(False)
            self.entry_penaltylogarray[i][10].set_active(False)
            for j in range(12):
                if j == 0:
                    self.entry_penaltylogarray[i][j].set_active(False)
                elif j == 1:
                    self.entry_penaltylogarray[i][j].set_active(False)
                elif j == 2 or j == 11:
                    self.entry_penaltylogarray[i][j].set_text("")
                else:
                    self.entry_penaltylogarray[i][j].set_active(False)

        self.entry_penaltylog_dialog_remark_referee.set_text("")
        self.entry_penaltylog_dialog_remark_scripter.set_text("")
        ####################################
        #

    def checkpenaltylogdata(self, widget, *data):
        global logdata_array
        global goal_can_be_increased
        global timeout_can_be_increased
        global timepenalty_can_be_activated
        global penalty_can_be_activated
        global warning_can_be_stored
        global penalty_can_be_activated_from_logdata
        global penalty_color_from_logdata
        global finally_identified_penalty_color_from_logdata
        #global penalty_can_be_activated_from_penaltylogdata
        #global penalty_color_from_penaltylogdata

        '''logic for checking the entries
        1.  set ok if goal can go up later (all conditions fulfilled)
        2.  set ok if timeout can go up later (all conditions ffulfilled
        3.  set ok if timepenalty can be activated later
        4.  second warning of a player: info message him to go to timepenalty
        5.  same line: B and W not clicked together
        6.  same player: no ejection and exchange together
        8.  same player: no ejection and timepenalty together
        9.  penalty / goal never together
        11. timepenalty and no W and no B and no nb: warning message
        12. warning and no B and no W and no nb given: warnmessage
        13. penalty: W or B must be given Error message
        15. player ejection: B or W and Nb must be given
        16. player change: warning B or W to be given (and indicate number)
        17. goal and no B and no W; additional info the Nb should be defined
        18. timeout clicked: warning message if no B and no W choosen
        19. player ejection and change not on the same line
        20. player ejection and timepenalty not on the same line
        21. same column: not > 1x goal penalty
        22. same player: not > 2x timepenalty
        23. same team 2x timeout
        24. 2x time warning same player
        25. timeout already at 1 and cannot be increased
        26. B or W clicked for timeout timepenalty goal warning penalty player ejec/change 
        28. when goal of other team and a player in timepenalty, release him
        '''
        # checkparam = data[1]
        # print("**  start checklogdata   **")
        # print("data", data)
        checkparam = data[0]
        checkarea = [0, 0]  # default: no search when nothing activated
        checkfokus = [0, 0]  # default: no search

        if checkparam == "all":
            checkfokus[0] = 9  # i line
            checkfokus[1] = 11  # j column
        else:
            checkfokus[0] = int(checkparam[2:4])  # "lpxx_yy"
            checkfokus[1] = int(checkparam[5:7])

        # print("checkparam",checkparam)

        # check1: result at the end
        goal_can_be_increased = True

        # check2: result at the end
        timeout_can_be_increased = True

        # ckeck3; result at the end
        timepenalty_can_be_activated = True

        penalty_can_be_activated = True

        #
        warning_can_be_stored = True

        self.label_penaltylog_dialog_message.set_text("")
        textmessage = ""

        # *************************************************************
        # read the log windows entries
        # test if anything was included in the log window, then store
        #
        print("checkfokus in penalty window: ", checkfokus)
        print("penalty_can_be_activated_from_logdata in penalty window", penalty_can_be_activated_from_logdata)
        if checkfokus[1] == 10 and penalty_can_be_activated_from_logdata:
            print("penalty color from logdata in penalty window",penalty_color_from_logdata)
            print("finally identified penalty color from logdata in penalty window",finally_identified_penalty_color_from_logdata)
            if finally_identified_penalty_color_from_logdata == "W":
                self.entry_penaltylogarray[checkfokus[0]][0].set_active(True)
            elif finally_identified_penalty_color_from_logdata== "B":
                self.entry_penaltylogarray[checkfokus[0]][1].set_active(True)
            else:
                print("penalty color was not indicated in log")
                pass

        if checkfokus[1] == 9 and penalty_can_be_activated_from_logdata:
            print("finally penalty color from logdata in penalty window: ",finally_identified_penalty_color_from_logdata)
            if finally_identified_penalty_color_from_logdata == "W":
                self.entry_penaltylogarray[checkfokus[0]][1].set_active(True)
            elif finally_identified_penalty_color_from_logdata == "B":
                self.entry_penaltylogarray[checkfokus[0]][0].set_active(True)
            else:
                print("penalty color was not indicated in log")
                pass

        #if checkfokus[1] == 10 and penalty_can_be_activated_from_penaltylogdata:
        #    if penalty_color_from_penaltylogdata == "W":
        #        self.entry_penaltylogarray[checkfofus[0]][0].set_active(True)
        #    else:
        #        self.entry_penaltylogarray[checkfofus[0]][1].set_active(True)


        for i in range(10):
            for j in range(12):
                if j == 0:
                    if self.entry_penaltylogarray[i][j].get_active():
                        logdata_array[i][j] = "B"

                        if i > checkarea[0]:
                            checkarea[0] = i
                        if j > checkarea[1]:
                            checkarea[1] = j

                    else:
                        logdata_array[i][j] = "_"
                elif j == 1:
                    if self.entry_penaltylogarray[i][j].get_active():
                        logdata_array[i][j] = "W"

                        if i > checkarea[0]:
                            checkarea[0] = i
                        if j > checkarea[1]:
                            checkarea[1] = j

                    else:
                        logdata_array[i][j] = "_"

                elif j == 2 or j == 11:

                    logdata_array[i][j] = self.entry_penaltylogarray[i][j].get_text()

                else:
                    if self.entry_penaltylogarray[i][j].get_active():
                        logdata_array[i][j] = "yes"

                        if i > checkarea[0]:
                            checkarea[0] = i
                        if j > checkarea[1]:
                            checkarea[1] = j

                    else:
                        logdata_array[i][j] = "_"

        #print("checkarea", checkarea)
        #print("checkfokus", checkfokus[0],checkfokus[1])

        # print("check 4")
        # check4
        # for i in range(10):
        if checkfokus[1] == 3 and checkfokus[0] <= checkarea[0]:
            for i in range(checkarea[0] + 1):
                if logdata_array[i][3] == "yes" and logdata_array[i][2] != "":
                    # check if already in warning list
                    self.label_penaltylog_dialog_message.set_text(
                        "I: check if already in warning list\n   then give timepalty")
                    # time.sleep(0.2)
        # print("check 5")
        # check 5
        if (checkfokus[1] == 0 or checkfokus[1] == 1) and checkfokus[0] <= checkarea[0]:
            for i in range(checkarea[0] + 1):
                if logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    self.label_penaltylog_dialog_message.set_text("E: B and W not on the same line")
                    if logdata_array[i][9] == "yes":
                        # penalty_can_be_activated_from_logdata = False
                        penalty_color_from_logdata = ""
                    elif (logdata_array[i][0] == "_" and logdata_array[i][1] == "_") and logdata_array[i][11] == "yes":
                        penalty_color_from_logdata = ""
                        self.label_log_dialog_message.set_text("W: B or W to be choosen for penalty")
                    elif (logdata_array[i][0] == "B" or logdata_array[i][1] == "W") and logdata_array[i][11] == "yes":
                        penalty_color_from_logdata = logdata_array[i][0]
                        if penalty_color_from_logdata == "_":
                            penalty_color_from_logdata = logdata_array[i][1]
                    else:
                        pass

                    # time.sleep(0.2)
        # print("check 6")
        # check 6
        if (checkfokus[1] == 5 or checkfokus[1] == 6) and checkfokus[0] <= checkarea[0]:
            for i in range(checkarea[0] + 1):
                if logdata_array[i][5] == "yes":  # player ejection detected; detect now if the same player is changed
                    for j in range(checkarea[0] + 1):
                        if logdata_array[j][6] == "yes":  # detect now if the same player is changed = nb in comment
                            if self.entry_penaltylogarray[j][11].get_text().find(self.entry_penaltylogarray[i][2].get_text()) != -1:
                                self.label_penaltylog_dialog_message.set_text(
                                    "E: player ejection and change not for same number")
                                # time.sleep(0.2)
        # print("check 8")
        # check 8
        if (checkfokus[1] == 5 or checkfokus[1] == 4) and checkfokus[0] <= checkarea[0]:
            for i in range(checkarea[0] + 1):
                if logdata_array[i][5] == "yes":  # player ejection detected; detect now if the same player is timepenalty
                    for j in range(checkarea[0] + 1):
                        if logdata_array[j][4] == "yes":  # detect now if the same player is changed = nb in comment
                            if self.entry_penaltylogarray[j][2].get_text() == self.entry_penaltylogarray[i][2].get_text():
                                self.label_penaltylog_dialog_message.set_text(
                                    "E: player ejection and timepenalty not for same number")
                                timepenalty_can_be_activated = False
                                # time.sleep(0.2)
        # print("check 11")
        # check11
        for i in range(checkarea[0] + 1):
            textmessage = ""

            if logdata_array[i][4] == "yes" and logdata_array[i][0] == "_" and \
                    logdata_array[i][1] == "_":
                textmessage = "E: choose B or W for timepenalty"
                timepenalty_can_be_activated = False

            if logdata_array[i][4] == "yes" and logdata_array[i][0] == "B" and \
                    logdata_array[i][1] == "W":
                textmessage = "E: B and W cannot be choosen together for timepenalty"
                timepenalty_can_be_activated = False

            if logdata_array[i][4] == "yes" and logdata_array[i][2] == "":
                textmessage = textmessage + "\nE: choose nb for timepenalty"
                timepenalty_can_be_activated = False

            if textmessage != "":
                self.label_penaltylog_dialog_message.set_text(textmessage)
                # time.sleep(0.2)

        # print("check 12")
        # check12
        if checkfokus[1] == 3 and checkfokus[0] <= checkarea[0]:
            textmessage = ""

            if logdata_array[i][3] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                textmessage = "E: choose B or W for player warning"

            if logdata_array[i][3] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                textmessage = "E: B and W cannot be choosen together for player warning"

            if logdata_array[i][3] == "yes" and logdata_array[i][2] == "":
                textmessage = textmessage + "\nW: choose nb for player warning"

            self.label_penaltylog_dialog_message.set_text(textmessage)

        # print("check 13")
        # check13
        if checkfokus[1] == 9 and checkfokus[0] <= checkarea[0]:
            if checkparam == "all":
                for i in range(checkarea[0] + 1):

                    if logdata_array[i][9] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                        self.label_penaltylog_dialog_message.set_text("W: choose B or W for penalty")
                        penalty_can_be_activated = False

                    if logdata_array[i][9] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                        self.label_penaltylog_dialog_message.set_text("W: B and W cannot be choosen together for penalty")
                        penalty_can_be_activated = False
            else:
                if logdata_array[checkfokus[0]][9] == "yes" and logdata_array[checkfokus[0]][0] == "_" and \
                        logdata_array[checkfokus[0]][1] == "_":
                    self.label_penaltylog_dialog_message.set_text("W: choose B or W for penalty")
                    penalty_can_be_activated = False

                elif logdata_array[checkfokus[0]][9] == "yes" and logdata_array[checkfokus[0]][0] == "B" and \
                        logdata_array[checkfokus[0]][1] == "W":
                    self.label_penaltylog_dialog_message.set_text("W: B and W cannot be choosen together for penalty")
                    penalty_can_be_activated = False

                else:
                    pass
                    #penalty_can_be_activated_from_penaltylogdata = True
                    #penalty_color_from_penaltylogdata = logdata_array[checkfokus[0]][1]
                    #if penalty_color_from_penaltylogdata == "_":
                    #    penalty_color_from_penaltylogdata = logdata_array[checkfokus[0]][0]

        # print("check 15")
        # check15
        if checkfokus[1] == 5 and checkfokus[0] <= checkarea[0]:
            # if checkparam == "all":
            for i in range(checkarea[0] + 1):

                textmessage = ""

                if logdata_array[i][5] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                    textmessage = "E: choose B or W for player ejection"

                if logdata_array[i][5] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    textmessage = "E: B and W cannot be choosen together for player ejection"

                if logdata_array[i][5] == "yes" and logdata_array[i][2] == "":
                    textmessage = textmessage + "\nE: choose nb for player ejection"

                self.label_penaltylog_dialog_message.set_text(textmessage)

        # print("check 16")
        # check16
        if checkfokus[1] == 6 and checkfokus[0] <= checkarea[0]:
            # if checkparam == "all":
            for i in range(checkarea[0] + 1):
                if logdata_array[i][6] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                    self.label_penaltylog_dialog_message.set_text("W: choose B or W for player change")
                # time.sleep(0.2)
                if logdata_array[i][6] == "yes" and logdata_array[i][2] == "":
                    self.label_penaltylog_dialog_message.set_text(
                        "W: choose nb for player going out left\nput new player number coming in comment ")
                # time.sleep(0.2)
                if logdata_array[i][6] == "yes" and logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    self.label_penaltylog_dialog_message.set_text(
                        "E: B and W cannot be choosen together for player change")
                # time.sleep(0.2)
        # print("check 17")
        # check17
        if checkfokus[1] == 10 and checkfokus[0] <= checkarea[0]:
            # if checkparam == "all":
            for i in range(checkarea[0] + 1):
                if logdata_array[i][10] == "yes":
                    textmessage = ""

                    if logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                        textmessage = "E: cannot choose B and W for goal"
                        goal_can_be_increased = False

                    if logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                        textmessage = "E: choose B or W for goal"
                        goal_can_be_increased = False

                    if logdata_array[i][2] == "":
                        textmessage = textmessage + "\nI: put nb of the player having scored"

                    self.label_penaltylog_dialog_message.set_text(textmessage)

        # print("check 18")
        # check18
        for i in range(checkarea[0] + 1):
            if logdata_array[i][7] == "yes" and logdata_array[i][0] == "_" and logdata_array[i][1] == "_":
                self.label_penaltylog_dialog_message.set_text("E: choose B or W for timeout")
                timeout_can_be_increased = False
                # time.sleep(0.2)
        # print("check 19")
        # check 19
        for i in range(checkarea[0] + 1):
            if logdata_array[i][5] == "yes" and logdata_array[i][6] == "yes":
                self.label_penaltylog_dialog_message.set_text("w: player ejection and change not on the same line")
                # time.sleep(0.2)
        # print("check 20")
        # check 20
        for i in range(checkarea[0] + 1):
            if logdata_array[i][4] == "yes" and logdata_array[i][5] == "yes":
                self.label_penaltylog_dialog_message.set_text("w: player ejection and timepenalty not on the same line")
                # time.sleep(0.2)

        event_detected = False
        for i in range(checkarea[0] + 1):
            if logdata_array[i][9] == "yes":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_penaltylog_dialog_message.set_text("E: not 2 times penalty")
                    penalty_can_be_activated = False
                # time.sleep(0.2)

        event_detected = False
        for i in range(checkarea[0] + 1):
            if logdata_array[i][10] == "yes":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_penaltylog_dialog_message.set_text("E: not 2 times goal")
                    goal_can_be_increased = False
                # time.sleep(0.2)
        #print("check 22")
        # check 22

        # print("check 9")
        # check 9
        event_detected = False

        penaltyevent_detected = False
        for i in range(checkarea[0] + 1):
            if logdata_array[i][9] == "yes" and not penaltyevent_detected:
                penaltyevent_detected = True
                if not event_detected:
                    event_detected = True
                else:
                    timeout_can_be_increased = False  # penalty seen but not correctly setup
                    self.label_penaltylog_dialog_message.set_text(
                        "E: not 2x penalty")
                    # time.sleep(0.2)

        goalevent_detected = False
        for i in range(checkarea[0] + 1):
            if logdata_array[i][10] == "yes" and not goalevent_detected:
                goalevent_detected = True
                if not event_detected:
                    event_detected = True
                else:
                    self.label_penaltylog_dialog_message.set_text(
                        "E: not 2x goal")
                    # time.sleep(0.2)

        # check 23
#!!!!!!!!!!!!!!!!!!!! 2x possible !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        event_detected = False
        for i in range(checkarea[0] + 1):
            if logdata_array[i][7] == "yes" and logdata_array[i][0] == "B":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_penaltylog_dialog_message.set_text("E: not 2 times timeout team blue")
                    timeout_can_be_increased = False

        event_detected = False
        for i in range(checkarea[0] + 1):
            if logdata_array[i][7] == "yes" and logdata_array[i][1] == "W":
                if not event_detected:
                    event_detected = True
                else:
                    self.label_penaltylog_dialog_message.set_text("E: not 2 times timeout team white")
                    timeout_can_be_increased = False

        #print("check 24")
        # check24

        # check25
        # print("check 25")
        for i in range(checkarea[0] + 1):
            if logdata_array[i][7] == "yes":

                if logdata_array[i][0] == "B":
                    if left_team_is_blue and self.spinbutton_timeout_left.get_value() == 1:
                        self.label_penaltylog_dialog_message.set_text(
                            "E: no additional timeout possible for team blue")
                        timeout_can_be_increased = False
                    if not left_team_is_blue and self.spinbutton_timeout_right.get_value() == 1:
                        self.label_penaltylog_dialog_message.set_text(
                            "E: no additional timeout possible for team blue")
                        timeout_can_be_increased = False

                if logdata_array[i][1] == "W":
                    if left_team_is_blue and self.spinbutton_timeout_right.get_value() == 1:
                        self.label_penaltylog_dialog_message.set_text(
                            "E: no additional timeout possible for team white")
                        timeout_can_be_increased = False
                    if not left_team_is_blue and self.spinbutton_timeout_left.get_value() == 1:
                        self.label_penaltylog_dialog_message.set_text(
                            "E: no additional timeout possible for team white")
                        timeout_can_be_increased = False

        # print("check 26")
        # check26
        if (checkfokus[1] == 0 or checkfokus[1] == 1) and checkfokus[0] <= checkarea[0]:
            # if checkparam == "all":
            for i in range(checkarea[0] + 1):
                if logdata_array[i][0] == "B" and logdata_array[i][1] == "W":
                    self.label_penaltylog_dialog_message.set_text("w: not B and W on the same line")
                elif logdata_array[i][0] != "B" and logdata_array[i][1] != "W":

                    if logdata_array[i][7] == "yes":
                        self.label_penaltylog_dialog_message.set_text("W: choose B or W of the team having timeout")
                        timeout_can_be_increased = False
                        #time.sleep(0.1)

                    if logdata_array[i][4] == "yes":
                        self.label_penaltylog_dialog_message.set_text("E: choose B or W for timepenalty")
                        timepenalty_can_be_activated = False
                        if logdata_array[i][2] == "":
                            self.label_penaltylog_dialog_message.set_text("E: choose nb for timepemalty")
                            timepenalty_can_be_activated = False

                    if logdata_array[i][12] == "yes":
                        self.label_penaltylog_dialog_message.set_text("W: choose B or W for goal")
                        goal_can_be_increased = False
                        #time.sleep(0.1)

                    if logdata_array[i][3] == "yes":
                        self.label_penaltylog_dialog_message.set_text("W: choose B or W for warning")
                        #time.sleep(0.1)
                        if logdata_array[i][2] == "":
                            self.label_penaltylog_dialog_message.set_text("E: choose nb for warning")
                            #time.sleep(0.1)

                    if logdata_array[i][11] == "yes":
                        self.label_penaltylog_dialog_message.set_text("E: choose B or W for penalty")
                        #time.sleep(0.1)

                    if logdata_array[i][5] == "yes":
                        self.label_penaltylog_dialog_message.set_text("W: choose B or W for player ejection")
                        #time.sleep(0.2)
                        if logdata_array[i][2] == "":
                            self.label_penaltylog_dialog_message.set_text("E: choose nb for player ejection")
                            #time.sleep(0.1)

                    if logdata_array[i][6] == "yes":
                        self.label_penaltylog_dialog_message.set_text("E: choose B or W for player change")

                elif logdata_array[i][0] != "B" or logdata_array[i][1] != "W":

                    if logdata_array[i][4] == "yes" and logdata_array[i][2] == "":
                        self.label_penaltylog_dialog_message.set_text("E: choose nb for timepemalty")
                        timepenalty_can_be_activated = False

                    if logdata_array[i][3] == "yes" and logdata_array[i][2] == "":
                        self.label_penaltylog_dialog_message.set_text("E: choose nb for warning")
                        #time.sleep(0.1)

                    if logdata_array[i][5] == "yes" and logdata_array[i][2] == "":
                        self.label_penaltylog_dialog_message.set_text("E: choose nb for player ejection")
                        #time.sleep(0.1)

                    if logdata_array[i][12] == "yes" and logdata_array[i][2] == "":
                        self.label_penaltylog_dialog_message.set_text("I: choose nb for goal")
                        #time.sleep(0.1)

        # print("check 27")
        # check27
        #if (checkfokus[1] == 9 or checkfokus[1] == 10) and checkfokus[0] <= checkarea[0]:

        #    for i in range(checkarea[0] + 1):

        #        if logdata_array[i][10] == "yes":
        #            if logdata_array[i][2] == "":
        #                self.label_penaltylog_dialog_message.set_text("I: choose nb player for goal")
                        #time.sleep(0.2)

        #        if logdata_array[i][3] == "yes":
        #            if logdata_array[i][2] == "":
        #                self.label_penaltylog_dialog_message.set_text("W: choose nb player for warning")
                        #time.sleep(0.2)

        #        if logdata_array[i][5] == "yes":
        #            if logdata_array[i][2] == "":
        #                self.label_penaltylog_dialog_message.set_text("E: choose nb for player ejection")
                        #time.sleep(0.2)

        #        if logdata_array[i][4] == "yes":
        #            if logdata_array[i][2] == "":
        #                self.label_penaltylog_dialog_message.set_text("E: choose nb for timepemalty")
        #                timepenalty_can_be_activated = False

#        print("**  end checkpenaltylogdata   **")

    def transferpenaltylog_to_board(self, widget, data=None):
        global goal_can_be_increased
        global timeout_can_be_increased
        global timepenalty_can_be_activated
        global penalty_can_be_activated
        global warning_can_be_stored
        global left_team_is_blue
        '''
        goal correctly recognized? -> activate it immediatly
        penalty correctly recognized? -> activate it and make ready for start
        timeout correctly recognized (no penalty identified) -> activate and start it
        timepenalty correctly recognized? -> activate it and make ready to start
        
        the assumption is all actions can be done because filtered and reconized already as free of log failure
        
        '''
        if goal_can_be_increased: # if present...
            for i in range(10):
                if logdata_array[i][10] == "yes":
                    # increase
                    if logdata_array[i][0] == "B":
                        if left_team_is_blue:
                            self.spinbutton_points_team_left.spin(0,1.0)
                        else:
                            self.spinbutton_points_team_right.spin(0,1.0)

                    if logdata_array[i][1] == "W":
                        if left_team_is_blue:
                            self.spinbutton_points_team_right.spin(0,1.0)
                        else:
                            self.spinbutton_points_team_left.spin(0,1.0)

        if penalty_can_be_activated: # if present...
            # activate
            for i in range(10):
                if logdata_array[i][9] == "yes":
                    # activate penalty
                    self.button_clearreset_special_time_sequence.set_active(True)
                    self.button_special_time_sequence_penalty.set_active(True)

                if i==9 and not self.button_special_time_sequence_penalty.get_active():
                    if timeout_can_be_increased: # if present..
                        for j in range(10):
                            if logdata_array[j][7] == "yes":
                                # activate timeout if timeout not already at 1

                                if logdata_array[j][0] == "B":
                                    if left_team_is_blue:
                                        #self.spinbutton_timeout_left.get_value()
                                        self.spinbutton_timeout_left.spin(0, 1.0)
                                    else:
                                        self.spinbutton_timeout_right.spin(0, 1.0)

                                if logdata_array[j][1] == "W":
                                    if left_team_is_blue:
                                        self.spinbutton_timeout_right.spin(0, 1.0)
                                    else:
                                        self.spinbutton_timeout_left.spin(0, 1.0)

                                self.button_special_time_sequence_timeout.set_active(True)
                                self.button_start_special_time_sequence.set_active(True)

        if timepenalty_can_be_activated:

            for i in range(10):
                if logdata_array[i][4] == "yes" and logdata_array[i][2]!="":

                    if left_team_is_blue:

                        if logdata_array[i][0] == "B":

                            if self.entry_name_penalty_player_1_left.get_text()=="":
                                self.entry_name_penalty_player_1_left.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_2_left.get_text()=="":
                                self.entry_name_penalty_player_2_left.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_3_left.get_text()=="":
                                self.entry_name_penalty_player_3_left.set_text(logdata_array[i][2])
                            else:
                                print("scoreboard full, timepenalty cannot be transfered into it")

                        else:
                            if self.entry_name_penalty_player_1_right.get_text()=="":
                                self.entry_name_penalty_player_1_right.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_2_right.get_text()=="":
                                self.entry_name_penalty_player_2_right.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_3_right.get_text()=="":
                                self.entry_name_penalty_player_3_right.set_text(logdata_array[i][2])
                            else:
                                print("scoreboard full, timepenalty cannot be transfered into it")

                    else:

                        if logdata_array[i][0] == "B":
                            if self.entry_name_penalty_player_1_right.get_text()=="":
                                self.entry_name_penalty_player_1_right.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_2_right.get_text()=="":
                                self.entry_name_penalty_player_2_right.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_3_right.get_text()=="":
                                self.entry_name_penalty_player_3_right.set_text(logdata_array[i][2])
                            else:
                                print("scoreboard full, timepenalty cannot be transfered into it")
                        else:
                            if self.entry_name_penalty_player_1_left.get_text()=="":
                                self.entry_name_penalty_player_1_left.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_2_left.get_text()=="":
                                self.entry_name_penalty_player_2_left.set_text(logdata_array[i][2])
                            elif self.entry_name_penalty_player_3_left.get_text()=="":
                                self.entry_name_penalty_player_3_left.set_text(logdata_array[i][2])
                            else:
                                print("scoreboard full, timepenalty cannot be transfered into it")

        if warning_can_be_stored:
            # future functionality
            pass

        if timeout_can_be_increased:
            pass

    def store_2lines_log(self, widget, data=None):
        global logfile_game
        global logfile_game_handler
        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            now = datetime.now()
            logfile_game_handler.write(
                "************************************************************************************************************************************\n")
            logfile_game_handler.write(
                "*  2 lines log                                                                                                                     *\n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                "*  2 lines log                                                                                                                     *\n")

            logfile_game_handler.write(
                "************************************************************************************************************************************\n")
            logfile_game_handler.write("at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
            logfile_game_handler.write("at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                  "at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

            logfile_game_handler.write("first line comment     : %-s\n" % (self.entry_anytime_line1intolog.get_text()))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                  "first line comment     : %-s\n" % (self.entry_anytime_line1intolog.get_text()))

            logfile_game_handler.write("second line comment    : %-s\n" % (self.entry_anytime_line2intolog.get_text()))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                  "second line comment    : %-s\n" % (self.entry_anytime_line2intolog.get_text()))

            logfile_game_handler.write(
                "************************************************************************************************************************************\n")
            logfile_game_handler.close()

    def datadialog_on(self, widget, data=None):
        if self.button_log_functionality_on.get_active():
            self.logdialog.show()

    def penaltydialog_on(self, widget, data=None):
        if self.button_log_functionality_on.get_active():
            self.penaltylogdialog.show()

    def change_value_pointsentry(self, widget, data=None):
        global logfile_game
        global logfile_game_handler
        #print("************************************")
        #print("**                                **")
        #print("**  if logging activated          **")
        #print("**   write down new point status  **")
        #print("**                                **")
        #print("************************************")
        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            logfile_game_handler.write("************* control board activity **************\n")
            logfile_game_handler.write("change point status \n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                  "change point status \n")

            now = datetime.now()
            logfile_game_handler.write    ("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
            logfile_game_handler.write    ("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

            if left_team_is_blue:
                #logfile_game_handler.write("  blue: %s    white: %s\n" % (self.label_control_points_team_left.get_text(),
                #                                                     self.label_control_points_team_right.get_text()))
                logfile_game_handler.write(
                    "  blue: %s    white: %s\n" % (str(int(self.spinbutton_points_team_left.get_value())),
                                                   str(int(self.spinbutton_points_team_right.get_value()))))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                    "  blue: %s    white: %s\n" % (str(int(self.spinbutton_points_team_left.get_value())),
                                                   str(int(self.spinbutton_points_team_right.get_value()))))

                #int(self.spinbutton_points_team_left.get_value())
            else:
                logfile_game_handler.write("  white: %s    blue: %s\n" % (str(int(self.spinbutton_points_team_left.get_value())),
                                                   str(int(self.spinbutton_points_team_right.get_value()))))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  white: %s    blue: %s\n" % (str(int(self.spinbutton_points_team_left.get_value())),
                                                   str(int(self.spinbutton_points_team_right.get_value()))))

            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()


    def change_value_timeoutentry(self, widget, data=None):
        global left_team_is_blue
        global logfile_game
        global logfile_game_handler

        #print("**************************************")
        #print("**                                  **")
        #print("**  if logging activated            **")
        #print("**   write down new timeout status  **")
        #print("**                                  **")
        #print("**************************************")

        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            logfile_game_handler.write("************* control board activity **************\n")
            logfile_game_handler.write("change timeout status  \n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "change timeout status  \n")

            now = datetime.now()
            logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
            logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

            if left_team_is_blue:
                logfile_game_handler.write("  timeout blue: %s   timeout white: %s\n" %
                                           (str(int(self.spinbutton_timeout_left.get_value())),
                                            str(int(self.spinbutton_timeout_right.get_value()))))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  timeout blue: %s   timeout white: %s\n" %
                                           (str(int(self.spinbutton_timeout_left.get_value())),
                                            str(int(self.spinbutton_timeout_right.get_value()))))

            else:
                logfile_game_handler.write("  timeout white: %s   timeout blue: %s\n" %
                                           (str(int(self.spinbutton_timeout_right.get_value())),
                                            str(int(self.spinbutton_timeout_left.get_value()))))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  timeout white: %s   timeout blue: %s\n" %
                                           (str(int(self.spinbutton_timeout_right.get_value())),
                                            str(int(self.spinbutton_timeout_left.get_value()))))

            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()

    def change_value_periodentry(self, widget, data=None):
        global logfile_game
        #print("*************************************")
        #print("**                                 **")
        #print("**  if logging activated           **")
        #print("**   write down new period status  **")
        #print("**                                 **")
        #print("*************************************")
        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            logfile_game_handler.write("************* control board activity **************\n")
            logfile_game_handler.write("change period status  \n")

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "change period status  \n")

            now = datetime.now()
            logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
            logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

            logfile_game_handler.write("  period new             : %s\n" % (str(int(self.spinbutton_period.get_value()))))

            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  period new             : %s\n" % (str(int(self.spinbutton_period.get_value()))))

            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()

    def save_scoreboard_settings(self, widget, data=None):
        global logfile_settings
        '''all time settings are stored into a separate file in order to have the possibility to restore
        the data when the scoreboard is closed and restarted later'''
        #
        now = datetime.now()
        logfile_settings = str(now.strftime("%Y%m%d")) + "-" + str(self.entry_tournament_name.get_text()) + ".settings"
        logfile_settings_handler = open(logfile_settings, 'w')
        logfile_settings_handler.write("%s\n" % (self.entry_tournament_name.get_text()))
        logfile_settings_handler.write("%s\n" % (self.entry_tournament_contact.get_text()))
        logfile_settings_handler.write("%s\n" % (str(self.spinbutton_period_time.get_value())))
        logfile_settings_handler.write("%s\n" % (str(self.spinbutton_penalty_duration.get_value())))
        logfile_settings_handler.write("%s\n" % (str(self.spinbutton_break_time.get_value())))
        logfile_settings_handler.write("%s\n" % (str(self.spinbutton_timeout.get_value())))
        logfile_settings_handler.write("%s\n" % (str(self.spinbutton_time_penalty.get_value())))
        logfile_settings_handler.write("%s\n" % (str(self.spinbutton_warning_timepenalty.get_value())))
        logfile_settings_handler.write("%s\n" % (str(self.spinbutton_warning_break_timeout.get_value())))
        logfile_settings_handler.write("%s\n" % (str(self.button_nostop_watch.get_active())))
        if self.button_nostop_watch.get_active():
            logfile_settings_handler.write("%s\n" % (str(self.spinbutton_add_time.get_value())))
        logfile_settings_handler.close()

    def restore_scoreboard_settings(self, widget, data=None):
        global logfile_settings
        '''all time settings stored in a separate file will be uploaded into the scoreboard'''
        #
        logfile_settings = self.ChooserButton_read_file_settings.get_filename()
        with open(logfile_settings) as logfile_settings_handler:
            lines = logfile_settings_handler.read().split("\n")
        self.entry_tournament_name.set_text(lines[0])
        self.entry_tournament_contact.set_text(lines[1])
        self.spinbutton_period_time.set_value(float(lines[2]))
        self.spinbutton_penalty_duration.set_value(float(lines[3]))
        self.spinbutton_break_time.set_value(float(lines[4]))
        self.spinbutton_timeout.set_value(float(lines[5]))
        self.spinbutton_time_penalty.set_value(float(lines[6]))
        self.spinbutton_warning_timepenalty.set_value(float(lines[7]))
        self.spinbutton_warning_break_timeout.set_value(float(lines[8]))
        if lines[9] == "True":
            self.button_nostop_watch.set_active(True)
            self.spinbutton_add_time.set_value(float(lines[10]))

    def activate_time_penalty_entry_player_1_left(self, widget, data=None):
        global running_time_penalty_player_1_left, time_penalty_player_1_left_initialized, \
            ellapsed_time_penalty_player_1_left_seconds, counter_seconds_time_penalty_player_1_left
        global logfile_game
        global left_team_is_blue
        if self.button_activate_timepenalty_player_1_left.get_active():
            if str(self.entry_name_penalty_player_1_left.get_text()) != "":

                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    if left_team_is_blue:
                        logfile_game_handler.write("activate timepenalty for player blue number %2s\n" % (str(self.entry_name_penalty_player_1_left.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "activate timepenalty for player blue number %2s\n" % (str(self.entry_name_penalty_player_1_left.get_text())))

                    else:
                        logfile_game_handler.write("activate timepenalty for player white number %2s\n" % (str(self.entry_name_penalty_player_1_left.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "activate timepenalty for player white number %2s\n" % (str(self.entry_name_penalty_player_1_left.get_text())))

                    logfile_game_handler.write    ("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                    logfile_game_handler.write    ("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()

                running_time_penalty_player_1_left = True
                time_penalty_player_1_left_initialized = False
                ellapsed_time_penalty_player_1_left_seconds = 0
                label_name = str(self.entry_name_penalty_player_1_left.get_text())
        #        print("   ")
        #        print("cap number of new timepenalty player  ", label_name)
        #        print("   ")
                # update counter label
                m, s = divmod(timepenalty_maximum_seconds, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_time_penalty_player_1_left.set_text(buffer_label_to_appear)

                if self.button_type_view_invertedcontrolview.get_active() \
                        and self.button_separate_game_view_on.get_active():
                    self.label_view_name_penalty_player_1_right.set_text(label_name)
                    self.label_view_time_penalty_player_1_right.set_text(buffer_label_to_appear)
                    counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds  # time countdown ready
                else:
                    self.label_view_name_penalty_player_1_left.set_text(label_name)
                    self.label_view_time_penalty_player_1_left.set_text(buffer_label_to_appear)
                    counter_seconds_time_penalty_player_1_left = timepenalty_maximum_seconds  # time countdown ready
            else:
                # buffer_label_to_appear = "nb cap?"
                # self.label_control_time_penalty_player_1_left.set_text(buffer_label_to_appear)
                # time.sleep(0.5)
                self.button_clear_timepenalty_player_1_left.set_active(True)
                #

    def clear_time_penalty_entry_player_1_left(self, widget, data=None):
        global logfile_game
        global left_team_is_blue
        global running_time_penalty_player_1_left, time_penalty_player_1_left_initialized, \
            ellapsed_time_penalty_player_1_left_seconds, \
            buffer_last_started_ellapsed_time_penalty_player_1_left_seconds, counter_seconds_time_penalty_player_1_left
        if self.button_clear_timepenalty_player_1_left.get_active():

            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                if left_team_is_blue:
                    logfile_game_handler.write("clear timepenalty for player blue number %2s\n" % (
                    str(self.entry_name_penalty_player_1_left.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "clear timepenalty for player blue number %2s\n" % (
                    str(self.entry_name_penalty_player_1_left.get_text())))

                else:
                    logfile_game_handler.write("clear timepenalty for player white number %2s\n" % (
                    str(self.entry_name_penalty_player_1_left.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "clear timepenalty for player white number %2s\n" % (
                    str(self.entry_name_penalty_player_1_left.get_text())))

                logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_1_left.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_1_left.get_text()))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()

            running_time_penalty_player_1_left = False
            time_penalty_player_1_left_initialized = False
            ellapsed_time_penalty_player_1_left_seconds = 0
            buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = 0
            # update counter label to 0
            self.label_control_time_penalty_player_1_left.set_text("00:00")
            self.label_control_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            counter_seconds_time_penalty_player_1_left = 0  # clear countdown
            self.entry_name_penalty_player_1_left.set_text("")  # clear name
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_1_right.set_text("")
                self.label_view_time_penalty_player_1_right.set_text("00:00")
            else:
                self.label_view_time_penalty_player_1_left.set_text("00:00")
                self.label_view_name_penalty_player_1_left.set_text("")
                #

    def activate_time_penalty_entry_player_2_left(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_2_left, time_penalty_player_2_left_initialized, \
            ellapsed_time_penalty_player_2_left_seconds, counter_seconds_time_penalty_player_2_left
        if self.button_activate_timepenalty_player_2_left.get_active():
            if str(self.entry_name_penalty_player_2_left.get_text()) != "":

                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    if left_team_is_blue:
                        logfile_game_handler.write("activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_2_left.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "*          pascaldagornet@yahoo.de                *\n")

                    else:
                        logfile_game_handler.write("activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_2_left.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_2_left.get_text())))

                    logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()


                running_time_penalty_player_2_left = True
                time_penalty_player_2_left_initialized = False
                ellapsed_time_penalty_player_2_left_seconds = 0
                label_name = str(self.entry_name_penalty_player_2_left.get_text())
        #        print("   ")
        #        print("cap number of new timepenalty player  ", label_name)
        #        print("   ")
                # update counter label
                m, s = divmod(timepenalty_maximum_seconds, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_time_penalty_player_2_left.set_text(buffer_label_to_appear)

                if self.button_type_view_invertedcontrolview.get_active() and \
                        self.button_separate_game_view_on.get_active():
                    self.label_view_name_penalty_player_2_right.set_text(label_name)
                    self.label_view_time_penalty_player_2_right.set_text(buffer_label_to_appear)
                    counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds  # time countdown ready
                else:
                    self.label_view_name_penalty_player_2_left.set_text(label_name)
                    self.label_view_time_penalty_player_2_left.set_text(buffer_label_to_appear)
                    counter_seconds_time_penalty_player_2_left = timepenalty_maximum_seconds  # time countdown ready
            else:
                # buffer_label_to_appear = "nb cap?"
                # self.label_control_time_penalty_player_2_left.set_text(buffer_label_to_appear)
                self.button_clear_timepenalty_player_2_left.set_active(True)
                #

    def clear_time_penalty_entry_player_2_left(self, widget, data=None):
        global logfile_game
        global left_team_is_blue
        global running_time_penalty_player_2_left, time_penalty_player_2_left_initialized, \
            ellapsed_time_penalty_player_2_left_seconds, \
            buffer_last_started_ellapsed_time_penalty_player_2_left_seconds, counter_seconds_time_penalty_player_2_left
        if self.button_clear_timepenalty_player_2_left.get_active():

            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                if left_team_is_blue:
                    logfile_game_handler.write("clear timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_2_left.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                               "clear timepenalty for player blue number %2s\n" % (
                                                              str(self.entry_name_penalty_player_2_left.get_text())))

                else:
                    logfile_game_handler.write("clear timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_2_left.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "clear timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_2_left.get_text())))

                logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_2_left.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_2_left.get_text()))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()

            running_time_penalty_player_2_left = False
            time_penalty_player_2_left_initialized = False
            ellapsed_time_penalty_player_2_left_seconds = 0
            buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = 0
            # update counter label to 0
            self.label_control_time_penalty_player_2_left.set_text("00:00")
            self.label_control_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            counter_seconds_time_penalty_player_2_left = 0  # clear countdown
            self.entry_name_penalty_player_2_left.set_text("")  # clear name
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_2_right.set_text("")
                self.label_view_time_penalty_player_2_right.set_text("00:00")
            else:
                self.label_view_time_penalty_player_2_left.set_text("00:00")
                self.label_view_name_penalty_player_2_left.set_text("")
        #

    def activate_time_penalty_entry_player_3_left(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_3_left, time_penalty_player_3_left_initialized, \
            ellapsed_time_penalty_player_3_left_seconds, counter_seconds_time_penalty_player_3_left
        if self.button_activate_timepenalty_player_3_left.get_active():
            if str(self.entry_name_penalty_player_3_left.get_text()) != "":


                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    if left_team_is_blue:
                        logfile_game_handler.write("activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_3_left.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_3_left.get_text())))

                    else:
                        logfile_game_handler.write("activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_3_left.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                   "activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_3_left.get_text())))

                    logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()



                running_time_penalty_player_3_left = True
                time_penalty_player_3_left_initialized = False
                ellapsed_time_penalty_player_3_left_seconds = 0
                label_name = str(self.entry_name_penalty_player_3_left.get_text())
        #        print("   ")
        #        print("cap number of new timepenalty player  ", label_name)
        #        print("   ")
                # update counter label
                m, s = divmod(timepenalty_maximum_seconds, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_time_penalty_player_3_left.set_text(buffer_label_to_appear)

                if self.button_type_view_invertedcontrolview.get_active() and \
                        self.button_separate_game_view_on.get_active():
                    self.label_view_name_penalty_player_3_right.set_text(label_name)
                    self.label_view_time_penalty_player_3_right.set_text(buffer_label_to_appear)
                    counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds  # time countdown ready
                else:
                    self.label_view_name_penalty_player_3_left.set_text(label_name)
                    self.label_view_time_penalty_player_3_left.set_text(buffer_label_to_appear)
                    counter_seconds_time_penalty_player_3_left = timepenalty_maximum_seconds  # time countdown ready
            else:
                # buffer_label_to_appear = "nb cap?"
                # self.label_control_time_penalty_player_3_left.set_text(buffer_label_to_appear)
                self.button_clear_timepenalty_player_3_left.set_active(True)
        #

    def clear_time_penalty_entry_player_3_left(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_3_left, time_penalty_player_3_left_initialized, \
            ellapsed_time_penalty_player_3_left_seconds, \
            buffer_last_started_ellapsed_time_penalty_player_3_left_seconds, counter_seconds_time_penalty_player_3_left
        if self.button_clear_timepenalty_player_3_left.get_active():

            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                if left_team_is_blue:
                    logfile_game_handler.write("clear timepenalty for player blue number %2s\n" % (
                        str(self.entry_name_penalty_player_3_left.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "clear timepenalty for player blue number %2s\n" % (
                        str(self.entry_name_penalty_player_3_left.get_text())))

                else:
                    logfile_game_handler.write("clear timepenalty for player white number %2s\n" % (
                        str(self.entry_name_penalty_player_3_left.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                             "clear timepenalty for player white number %2s\n" % (
                        str(self.entry_name_penalty_player_3_left.get_text())))

                logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                           "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_3_left.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_3_left.get_text()))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()


            running_time_penalty_player_3_left = False
            time_penalty_player_3_left_initialized = False
            ellapsed_time_penalty_player_3_left_seconds = 0
            buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = 0
            # update counter label to 0
            self.label_control_time_penalty_player_3_left.set_text("00:00")
            self.label_control_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            counter_seconds_time_penalty_player_3_left = 0  # clear countdown
            self.entry_name_penalty_player_3_left.set_text("")  # clear name
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_3_right.set_text("")
                self.label_view_time_penalty_player_3_right.set_text("00:00")
            else:
                self.label_view_time_penalty_player_3_left.set_text("00:00")
                self.label_view_name_penalty_player_3_left.set_text("")

    def activate_time_penalty_entry_player_1_right(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_1_right, time_penalty_player_1_right_initialized, \
            ellapsed_time_penalty_player_1_right_seconds, counter_seconds_time_penalty_player_1_right
        if self.button_activate_timepenalty_player_1_right.get_active():
            if str(self.entry_name_penalty_player_1_right.get_text()) != "":


                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    if left_team_is_blue:
                        logfile_game_handler.write("activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_1_right.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_1_right.get_text())))

                    else:
                        logfile_game_handler.write("activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_1_right.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_1_right.get_text())))

                    logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()


                running_time_penalty_player_1_right = True
                time_penalty_player_1_right_initialized = False
                ellapsed_time_penalty_player_1_right_seconds = 0
                label_name = str(self.entry_name_penalty_player_1_right.get_text())
        #        print("   ")
        #        print("cap number of new timepenalty player  ", label_name)
        #        print("   ")
                # update counter label
                m, s = divmod(timepenalty_maximum_seconds, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_time_penalty_player_1_right.set_text(buffer_label_to_appear)
                counter_seconds_time_penalty_player_1_right = timepenalty_maximum_seconds  # time countdown ready
                if self.button_type_view_invertedcontrolview.get_active() \
                        and self.button_separate_game_view_on.get_active():
                    self.label_view_name_penalty_player_1_left.set_text(label_name)
                    self.label_view_time_penalty_player_1_left.set_text(buffer_label_to_appear)
                else:
                    self.label_view_name_penalty_player_1_right.set_text(label_name)
                    self.label_view_time_penalty_player_1_right.set_text(buffer_label_to_appear)
            else:
                # buffer_label_to_appear = "nb cap?"
                # self.label_control_time_penalty_player_1_right.set_text(buffer_label_to_appear)
                self.button_clear_timepenalty_player_1_right.set_active(True)
        #

    def clear_time_penalty_entry_player_1_right(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_1_right, time_penalty_player_1_right_initialized, \
            ellapsed_time_penalty_player_1_right_seconds, \
            buffer_last_started_ellapsed_time_penalty_player_1_right_seconds, counter_seconds_time_penalty_player_1_right
        if self.button_clear_timepenalty_player_1_right.get_active():

            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                if left_team_is_blue:
                    logfile_game_handler.write("clear timepenalty for player white number %2s\n" % (
                        str(self.entry_name_penalty_player_1_right.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "clear timepenalty for player white number %2s\n" % (
                        str(self.entry_name_penalty_player_1_right.get_text())))

                else:
                    logfile_game_handler.write("clear timepenalty for player blue number %2s\n" % (
                        str(self.entry_name_penalty_player_1_right.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "clear timepenalty for player blue number %2s\n" % (
                        str(self.entry_name_penalty_player_1_right.get_text())))

                logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_1_right.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_1_right.get_text()))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()


            running_time_penalty_player_1_right = False
            time_penalty_player_1_right_initialized = False
            ellapsed_time_penalty_player_1_right_seconds = 0
            buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = 0
            # update counter label to 0
            self.label_control_time_penalty_player_1_right.set_text("00:00")
            self.label_control_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            counter_seconds_time_penalty_player_1_right = 0  # clear countdown
            self.entry_name_penalty_player_1_right.set_text("")  # clear name
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_1_left.set_text("")
                self.label_view_time_penalty_player_1_left.set_text("00:00")
            else:
                self.label_view_time_penalty_player_1_right.set_text("00:00")
                self.label_view_name_penalty_player_1_right.set_text("")

    def activate_time_penalty_entry_player_2_right(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_2_right, time_penalty_player_2_right_initialized, \
            ellapsed_time_penalty_player_2_right_seconds, counter_seconds_time_penalty_player_2_right
        if self.button_activate_timepenalty_player_2_right.get_active():
            if str(self.entry_name_penalty_player_2_right.get_text()) != "":


                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    if left_team_is_blue:
                        logfile_game_handler.write("activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_2_right.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "activate timepenalty for player white number %2s\n" % (
                                                                  str(
                                                                      self.entry_name_penalty_player_2_right.get_text())))

                    else:
                        logfile_game_handler.write("activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_2_right.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_2_right.get_text())))

                    logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()


                running_time_penalty_player_2_right = True
                time_penalty_player_2_right_initialized = False
                ellapsed_time_penalty_player_2_right_seconds = 0
                label_name = str(self.entry_name_penalty_player_2_right.get_text())
        #        print("   ")
        #        print("cap number of new timepenalty player  ", label_name)
        #        print("   ")
                # update counter label
                m, s = divmod(timepenalty_maximum_seconds, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_time_penalty_player_2_right.set_text(buffer_label_to_appear)
                counter_seconds_time_penalty_player_2_right = timepenalty_maximum_seconds  # time countdown ready
                if self.button_type_view_invertedcontrolview.get_active() \
                        and self.button_separate_game_view_on.get_active():
                    self.label_view_name_penalty_player_2_left.set_text(label_name)
                    self.label_view_time_penalty_player_2_left.set_text(buffer_label_to_appear)
                else:
                    self.label_view_name_penalty_player_2_right.set_text(label_name)
                    self.label_view_time_penalty_player_2_right.set_text(buffer_label_to_appear)
            else:
                # buffer_label_to_appear = "nb cap?"
                # self.label_control_time_penalty_player_2_right.set_text(buffer_label_to_appear)
                self.button_clear_timepenalty_player_2_right.set_active(True)
        #

    def clear_time_penalty_entry_player_2_right(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_2_right, time_penalty_player_2_right_initialized, \
            ellapsed_time_penalty_player_2_right_seconds, \
            buffer_last_started_ellapsed_time_penalty_player_2_right_seconds, counter_seconds_time_penalty_player_2_right
        if self.button_clear_timepenalty_player_2_right.get_active():

            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                if left_team_is_blue:
                    logfile_game_handler.write("clear timepenalty for player white number %2s\n" % (
                        str(self.entry_name_penalty_player_2_right.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "clear timepenalty for player white number %2s\n" % (
                        str(self.entry_name_penalty_player_2_right.get_text())))

                else:
                    logfile_game_handler.write("clear timepenalty for player blue number %2s\n" % (
                        str(self.entry_name_penalty_player_2_right.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "clear timepenalty for player blue number %2s\n" % (
                        str(self.entry_name_penalty_player_2_right.get_text())))

                logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_2_right.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_2_right.get_text()))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()


            running_time_penalty_player_2_right = False
            time_penalty_player_2_right_initialized = False
            ellapsed_time_penalty_player_2_right_seconds = 0
            buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = 0
            # update counter label to 0
            self.label_control_time_penalty_player_2_right.set_text("00:00")
            self.label_control_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                         gdk.RGBA(0, 0, 0, 1))
            counter_seconds_time_penalty_player_2_right = 0  # clear countdown
            self.entry_name_penalty_player_2_right.set_text("")  # clear name
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_2_left.set_text("")
                self.label_view_time_penalty_player_2_left.set_text("00:00")
            else:
                self.label_view_time_penalty_player_2_right.set_text("00:00")
                self.label_view_name_penalty_player_2_right.set_text("")

    def activate_time_penalty_entry_player_3_right(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_3_right, time_penalty_player_3_right_initialized, \
            ellapsed_time_penalty_player_3_right_seconds, counter_seconds_time_penalty_player_3_right
        if self.button_activate_timepenalty_player_3_right.get_active():
            if str(self.entry_name_penalty_player_3_right.get_text()) != "":

                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    if left_team_is_blue:
                        logfile_game_handler.write("activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_3_right.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "activate timepenalty for player white number %2s\n" % (
                            str(self.entry_name_penalty_player_3_right.get_text())))

                    else:
                        logfile_game_handler.write("activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_3_right.get_text())))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "activate timepenalty for player blue number %2s\n" % (
                            str(self.entry_name_penalty_player_3_right.get_text())))

                    logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()


                running_time_penalty_player_3_right = True
                time_penalty_player_3_right_initialized = False
                ellapsed_time_penalty_player_3_right_seconds = 0
                label_name = str(self.entry_name_penalty_player_3_right.get_text())
        #        print("   ")
        #        print("cap number of new timepenalty player  ", label_name)
        #        print("   ")
                # update counter label
                m, s = divmod(timepenalty_maximum_seconds, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_time_penalty_player_3_right.set_text(buffer_label_to_appear)
                counter_seconds_time_penalty_player_3_right = timepenalty_maximum_seconds  # time countdown ready
                if self.button_type_view_invertedcontrolview.get_active() \
                        and self.button_separate_game_view_on.get_active():
                    self.label_view_name_penalty_player_3_left.set_text(label_name)
                    self.label_view_time_penalty_player_3_left.set_text(buffer_label_to_appear)
                else:
                    self.label_view_name_penalty_player_3_right.set_text(label_name)
                    self.label_view_time_penalty_player_3_right.set_text(buffer_label_to_appear)
            else:
                # buffer_label_to_appear = "nb cap?"
                # self.label_control_time_penalty_player_3_right.set_text(buffer_label_to_appear)
                self.button_clear_timepenalty_player_3_right.set_active(True)
        #

    def clear_time_penalty_entry_player_3_right(self, widget, data=None):
        global logfile_game
        global running_time_penalty_player_3_right, time_penalty_player_3_right_initialized, \
            ellapsed_time_penalty_player_3_right_seconds, \
            buffer_last_started_ellapsed_time_penalty_player_3_right_seconds, counter_seconds_time_penalty_player_3_right
        if self.button_clear_timepenalty_player_3_right.get_active():

            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                if left_team_is_blue:
                    logfile_game_handler.write("clear timepenalty for player white number %2s\n" % (
                        str(self.entry_name_penalty_player_3_right.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "clear timepenalty for player white number %2s\n" % (
                        str(self.entry_name_penalty_player_3_right.get_text())))

                else:
                    logfile_game_handler.write("clear timepenalty for player blue number %2s\n" % (
                        str(self.entry_name_penalty_player_3_right.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "clear timepenalty for player blue number %2s\n" % (
                        str(self.entry_name_penalty_player_3_right.get_text())))

                logfile_game_handler.write("  at time                : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_3_right.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "  at player countdown    : %s min:s\n" % (self.label_control_time_penalty_player_3_right.get_text()))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()


            running_time_penalty_player_3_right = False
            time_penalty_player_3_right_initialized = False
            ellapsed_time_penalty_player_3_right_seconds = 0
            buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = 0
            # update counter label to 0
            self.label_control_time_penalty_player_3_right.set_text("00:00")
            self.label_control_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,gdk.RGBA(0, 0, 0, 1))
            counter_seconds_time_penalty_player_3_right = 0  # clear countdown
            self.entry_name_penalty_player_3_right.set_text("")  # clear name
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_3_left.set_text("")
                self.label_view_time_penalty_player_3_left.set_text("00:00")
            else:
                self.label_view_time_penalty_player_3_right.set_text("00:00")
                self.label_view_name_penalty_player_3_right.set_text("")

    #
    ############################################################################################
    # setting page
    ############################################################################################
    #
    def save_setting_changes(self, widget, data=None):
        global period_time_in_second_orig
        global period_time_in_second
        global timepenalty_maximum_seconds
        global penalty_maximum_seconds
        global timeout_maximum_seconds
        global break_maximum_seconds
        global left_team_is_blue
        global add_time_seconds
        global warning_timepenalty
        global warning_break_timeout
        global logfile_game
        global watch_stop
        #
        '''transfer immediatly the changes which were made in the setting window, into the control and view window'''
        #
        #print("transfer immediatly the changes which were made in the setting window, into the control window")
        #
        # update main counter label to maximum allowed time
        counter_seconds = 60 * int(self.spinbutton_period_time.get_value())
        period_time_in_second_orig = counter_seconds
        period_time_in_second = period_time_in_second_orig
        m, s = divmod(counter_seconds, 60)
        buffer_label_to_appear = "%02d:%02d" % (m, s)
        self.label_control_current_time.set_text(buffer_label_to_appear)
        self.label_view_current_time.set_text(buffer_label_to_appear)
        #
        # update timepenalty label players to zero
        buffer_label_to_appear = "00:00"
        self.label_control_time_penalty_player_1_left.set_text(buffer_label_to_appear)
        self.label_control_time_penalty_player_2_left.set_text(buffer_label_to_appear)
        self.label_control_time_penalty_player_3_left.set_text(buffer_label_to_appear)
        self.label_control_time_penalty_player_1_right.set_text(buffer_label_to_appear)
        self.label_control_time_penalty_player_2_right.set_text(buffer_label_to_appear)
        self.label_control_time_penalty_player_3_right.set_text(buffer_label_to_appear)
        #
        self.label_view_time_penalty_player_1_left.set_text(buffer_label_to_appear)
        self.label_view_time_penalty_player_2_left.set_text(buffer_label_to_appear)
        self.label_view_time_penalty_player_3_left.set_text(buffer_label_to_appear)
        self.label_view_time_penalty_player_1_right.set_text(buffer_label_to_appear)
        self.label_view_time_penalty_player_2_right.set_text(buffer_label_to_appear)
        self.label_view_time_penalty_player_3_right.set_text(buffer_label_to_appear)
        #
        timepenalty_maximum_seconds = 60 * int(self.spinbutton_time_penalty.get_value())
        penalty_maximum_seconds = int(self.spinbutton_penalty_duration.get_value())
        timeout_maximum_seconds = 60 * int(self.spinbutton_timeout.get_value())
        break_maximum_seconds = 60 * int(self.spinbutton_break_time.get_value())
        #
        if left_team_is_blue:
            self.label_control_team_name_left.set_text(self.entry_team_blue_name.get_text())
            self.label_control_team_name_right.set_text(self.entry_team_white_name.get_text())
            if self.button_type_view_copycontrolview.get_active():
                self.label_view_team_name_left.set_text(self.entry_team_blue_name.get_text())
                self.label_view_team_name_right.set_text(self.entry_team_white_name.get_text())
            else:
                self.label_view_team_name_right.set_text(self.entry_team_blue_name.get_text())
                self.label_view_team_name_left.set_text(self.entry_team_white_name.get_text())
        else:
            self.label_control_team_name_left.set_text(self.entry_team_white_name.get_text())
            self.label_control_team_name_right.set_text(self.entry_team_blue_name.get_text())
            if self.button_type_view_copycontrolview.get_active():
                self.label_view_team_name_left.set_text(self.entry_team_white_name.get_text())
                self.label_view_team_name_right.set_text(self.entry_team_blue_name.get_text())
            else:
                self.label_view_team_name_right.set_text(self.entry_team_white_name.get_text())
                self.label_view_team_name_left.set_text(self.entry_team_blue_name.get_text())
        #
        self.label_control_tournament_name.set_text(self.entry_tournament_name.get_text())
        self.label_control_tournament_contact.set_text(self.entry_tournament_contact.get_text())
        self.label_view_tournament_name.set_text(self.entry_tournament_name.get_text())
        self.label_view_tournament_contact.set_text(self.entry_tournament_contact.get_text())
        #
        watch_stop=self.button_stop_watch.get_active()
        add_time_seconds = 60*int(self.spinbutton_add_time.get_value())
        warning_timepenalty = int(self.spinbutton_warning_timepenalty.get_value())
        warning_break_timeout = int(self.spinbutton_warning_break_timeout.get_value())

        #
    def log_setting_changes(self, widget, data=None):
        global period_time_in_second_orig
        global period_time_in_second
        global timepenalty_maximum_seconds
        global penalty_maximum_seconds
        global timeout_maximum_seconds
        global break_maximum_seconds
        global left_team_is_blue
        global add_time_seconds
        global warning_timepenalty
        global warning_break_timeout
        global logfile_game
        global watch_stop
        #
        '''log the settings into the log file; it is called from the start_stop method'''
        #
        # update main counter label to maximum allowed time
        counter_seconds = 60 * int(self.spinbutton_period_time.get_value())
        period_time_in_second_orig = counter_seconds
        period_time_in_second = period_time_in_second_orig
        m, s = divmod(counter_seconds, 60)
        buffer_label_to_appear = "%02d:%02d" % (m, s)
        #
        timepenalty_maximum_seconds = 60 * int(self.spinbutton_time_penalty.get_value())
        penalty_maximum_seconds = int(self.spinbutton_penalty_duration.get_value())
        timeout_maximum_seconds = 60 * int(self.spinbutton_timeout.get_value())
        break_maximum_seconds = 60 * int(self.spinbutton_break_time.get_value())
        #
        watch_stop=self.button_stop_watch.get_active()
        add_time_seconds = 60*int(self.spinbutton_add_time.get_value())
        warning_timepenalty = int(self.spinbutton_warning_timepenalty.get_value())
        warning_break_timeout = int(self.spinbutton_warning_break_timeout.get_value())

        if self.button_log_functionality_on.get_active():

            # all VDST official default times are hard coded here
            #period_time_default_minutes = 15  # min  the label in the time view will be 00:00 text min:sec
            #warning_default_timepenalty = 10  # blinking of time penalty starts 10s from end
            #break_time_default_minutes = 5  # min the label in the time view will be 00:00 text min:sec
            #penalty_duration_default_seconds = 45  # s the label in the time view will be 00 text sec
            #timeout_default_minutes = 1  # min the label in the time view will be 00:00 text min:sec
            #time_penalty_default_minutes = 2  # min the label in the time view will be 00:00 text min:sec
            #number_of_period = 2
            #watch_stop_default = True
            #add_time_seconds = 0



            logfile_game_handler = open(logfile_game, 'a')
            now = datetime.now()
            logfile_game_handler.write("************** logging the settings ***************\n")
            logfile_game_handler.write("at time: %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

            logfile_game_handler.write("  period time        : %s s  " % (str(period_time_in_second)))
            if period_time_in_second != (period_time_default_minutes*60):
                logfile_game_handler.write("(VDST: %s s)\n" % (str(period_time_default_minutes*60)))
            else:
                logfile_game_handler.write("\n")

            logfile_game_handler.write("  timepenalty        : %s s  " % (str(timepenalty_maximum_seconds)))
            if timepenalty_maximum_seconds != (time_penalty_default_minutes*60):
                logfile_game_handler.write("(VDST: %s s)\n" % (str(time_penalty_default_minutes*60)))
            else:
                logfile_game_handler.write("\n")

            logfile_game_handler.write("  penalty            : %s s  " % (str(penalty_maximum_seconds)))
            if penalty_maximum_seconds != (penalty_duration_default_seconds):
                logfile_game_handler.write("(VDST: %s s)\n" % (str(penalty_duration_default_seconds)))
            else:
                logfile_game_handler.write("\n")

            logfile_game_handler.write("  timeout            : %s s  " % (str(timeout_maximum_seconds)))
            if timeout_maximum_seconds != (timeout_default_minutes*60):
                logfile_game_handler.write("(VDST: %s s)\n" % (str(timeout_default_minutes*60)))
            else:
                logfile_game_handler.write("\n")

            logfile_game_handler.write("  break              : %s s  " % (str(break_maximum_seconds)))
            if break_maximum_seconds != (break_time_default_minutes*60):
                logfile_game_handler.write("(VDST: %s s)\n" % (str(break_time_default_minutes*60)))
            else:
                logfile_game_handler.write("\n")

            logfile_game_handler.write("  blue team          : %s\n" % (str(self.entry_team_blue_name.get_text())))
            logfile_game_handler.write("  white team         : %s\n" % (str(self.entry_team_white_name.get_text())))
            if left_team_is_blue:
                logfile_game_handler.write("    blue left, white right\n")
            else:
                logfile_game_handler.write("    blue right, white left\n")

            logfile_game_handler.write("  tournament name    : %s\n" % (str(self.entry_tournament_name.get_text())))
            logfile_game_handler.write("  tournament contact : %s\n" % (str(self.entry_tournament_contact.get_text())))
            logfile_game_handler.write("  warning timepenalty: %s s\n" % (str(int(self.spinbutton_warning_timepenalty.get_value()))))
            logfile_game_handler.write("  warning break/time : %s s\n" % (str(int(self.spinbutton_warning_break_timeout.get_value()))))

            logfile_game_handler.write("  stop watch         : %s  " % (str(self.button_stop_watch.get_active())))
            if self.button_stop_watch.get_active():
                logfile_game_handler.write("\n")
            else:
                logfile_game_handler.write("(VDST: Yes)\n")
                logfile_game_handler.write(
                    "  (add time          : %s min)\n\n" % (str(int(self.spinbutton_add_time.get_value()))))

            logfile_game_handler.write("remark: 900s=15min 600s=10min 300s=5min\n")
            logfile_game_handler.write("        180s=3min  120s=2min  60s=1min\n\n")
            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()


    def clear_setting_time_data(self, widget, data=None):
        global period_time_default_minutes
        global period_time_in_second
        global break_time_default_minutes
        global penalty_duration_default_seconds
        global timeout_default_minutes
        global time_penalty_default_minutes
        global timepenalty_maximum_seconds
        global penalty_maximum_seconds
        global timeout_maximum_seconds
        global break_maximum_seconds
        global warning_default_timepenalty
        global warning_timepenalty
        global warning_break_timeout
        global warning_default_break_timeout
        global logfile_game
        global watch_stop
        #
        '''set back to default VDST time'''
        #print("set back to default VDST time")
        #
        self.spinbutton_period_time.set_value(period_time_default_minutes)
        self.spinbutton_break_time.set_value(break_time_default_minutes)
        self.spinbutton_penalty_duration.set_value(penalty_duration_default_seconds)
        self.spinbutton_timeout.set_value(timeout_default_minutes)
        self.spinbutton_time_penalty.set_value(time_penalty_default_minutes)
        self.spinbutton_warning_timepenalty.set_value(warning_default_timepenalty)
        self.spinbutton_warning_break_timeout.set_value(warning_default_break_timeout)
        #
        self.button_stop_watch.set_active(True)
        self.watch_stop_yes(self)
        #        print(self.comboboxtext_watch_stop.get_active_text()) # functionality not activ for now..
        # would allow a non stopped timing for penalty and free and ..
        #
        timepenalty_maximum_seconds = 60 * int(time_penalty_default_minutes)
        penalty_maximum_seconds = int(penalty_duration_default_seconds)
        timeout_maximum_seconds = 60 * int(timeout_default_minutes)
        break_maximum_seconds = 60 * (break_time_default_minutes)
        warning_timepenalty = warning_default_timepenalty
        #
        if self.button_log_functionality_on.get_active():
            logfile_game_handler = open(logfile_game, 'a')
            now = datetime.now()
            logfile_game_handler.write("************* control board activity **************\n")
            logfile_game_handler.write("restore VDST settings\n")
            logfile_game_handler.write("at time               : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
            logfile_game_handler.write("  period time         : %s s\n" % (str(period_time_in_second)))
            logfile_game_handler.write("  timepenalty         : %s s\n" % (str(timepenalty_maximum_seconds)))
            logfile_game_handler.write("  penalty             : %s s\n" % (str(penalty_maximum_seconds)))
            logfile_game_handler.write("  timeout             : %s s\n" % (str(timeout_maximum_seconds)))
            logfile_game_handler.write("  break               : %s s\n" % (str(break_maximum_seconds)))
            logfile_game_handler.write("  warning timepenalty : %s s\n" % (str(warning_default_timepenalty)))
            logfile_game_handler.write("  warning break/time  : %s s\n" % (str(warning_default_break_timeout)))
            logfile_game_handler.write("  stop watch activ    : yes\n")
            logfile_game_handler.write("***************************************************\n")
            logfile_game_handler.close()

        #

    def update_timer_labels(self, widget, data=None):
        global logfile_game
        global game_started
        global watch_stop
        global now_dont_stop
        global running_timeout
        global running_break
        global running_penalty
        global counter_seconds_board
        global period_time_in_second
        global action_start_time_of_the_game_is_ACTIVE
        global counter_seconds_special_time_sequence
        global stopped_special_time_sequence
        global buffer_last_time_start
        global buffer_last_started_ellapsed_period_time_seconds
        global timepenalty_maximum_seconds
        global buffer_last_started_ellapsed_time_penalty_player_1_left_seconds
        global counter_seconds_time_penalty_player_1_left
        global buffer_last_started_ellapsed_time_penalty_player_2_left_seconds
        global counter_seconds_time_penalty_player_2_left
        global buffer_last_started_ellapsed_time_penalty_player_3_left_seconds
        global counter_seconds_time_penalty_player_3_left
        global buffer_last_started_ellapsed_time_penalty_player_1_right_seconds
        global counter_seconds_time_penalty_player_1_right
        global buffer_last_started_ellapsed_time_penalty_player_2_right_seconds
        global counter_seconds_time_penalty_player_2_right
        global buffer_last_started_ellapsed_time_penalty_player_3_right_seconds
        global counter_seconds_time_penalty_player_3_right
        global warning_timepenalty

        '''Update of all timer labels and start/stop button label when necessary
        no time calculation here
        timecalculation made in the method run'''
        #
        # first the main time counter timer = period timer
        #
        #print("update_all_8_text_timer_labels")
        #
        if not game_started:
            # put into the label the period time setting
            #buffer_last_started_ellapsed_period_time_seconds = 0
            #period_time_in_second = 60 * int(self.spinbutton_period_time.get_value())
            #counter_seconds_board = period_time_in_second
            self.togglebutton_start_stop_game.set_label('START Time')
            #
        #print("def update_timer_labels: counter_seconds_board is ", counter_seconds_board)

        #if self.button_nostop_watch.get_active(): then blink when no stop at all anymore (add_time consumed)
        #    if counter_seconds_board > 0 and ellapsed_period_time_seconds > (period_time_in_second + add_time_seconds):
        #        m, s = divmod(counter_seconds_board, 60)
        #        buffer_label_to_appear = "%02d:%02d" % (m, s)
        #    else:
        #        buffer_label_to_appear = "over"
        #        if action_start_time_of_the_game_is_ACTIVE:
        #            time.sleep(0.5)
        #            self.togglebutton_start_stop_game.set_active(True)
        #            action_start_time_of_the_game_is_ACTIVE = False
        #            self.togglebutton_start_stop_game.set_label('START Time')

        if counter_seconds_board > 0:
            m, s = divmod(counter_seconds_board, 60)
            buffer_label_to_appear = "%02d:%02d" % (m, s)

            # no stop_watch means
            # - special mode where the watch dont stop (friendly games with major time restriction)
            # - the watch will not stop if the possible add_time_seconds is already used up by game stops
            # - if the watch is stopped, and the add_time is overdue, the watch will start automatically and will
            #   not stop; except the timing is resetted in the "tool" window
            # - if the watch is set to maximum counter and from the beginning, there is no add_time

            # stop watch means start/stop activ as standard

            if not watch_stop and (counter_seconds_board!=period_time_in_second or game_started):
                # if nostop watch, special sequences to start; stop button can become inactiv
                # counter_seconds_board!=period_time_in_second for the clock not to run when the time reset is activated

                if (ellapsed_time_game_in_seconds - ellapsed_period_time_seconds)>= add_time_seconds:
                    # blinking of the counter done here
                    m, s = divmod(ellapsed_time_game_in_seconds, 2)
                    if s > 0:  # grey letters
                        self.label_control_current_time.override_color(gtk.StateFlags.NORMAL,
                                                                                    gdk.RGBA(0, 0, 0, 0.6))
                        self.label_view_current_time.override_color(gtk.StateFlags.NORMAL,
                                                                                    gdk.RGBA(0, 0, 0, 0.6))
                    else:  # black letters
                        self.label_control_current_time.override_color(gtk.StateFlags.NORMAL,
                                                                                    gdk.RGBA(0, 0, 0, 1))
                        self.label_view_current_time.override_color(gtk.StateFlags.NORMAL,
                                                                                    gdk.RGBA(0, 0, 0, 1))

                    # counter_seconds_board != period_time_in_second:
                    self.togglebutton_start_stop_game.set_label('noSTOP')

                    #self.togglebutton_start_stop_game.set_active(False)
                    # dont do anything. the game must run and the start stop button must become inactiv
                    #


            else:
                self.label_control_current_time.override_color(gtk.StateFlags.NORMAL,
                                                               gdk.RGBA(0, 0, 0, 1))
                self.label_view_current_time.override_color(gtk.StateFlags.NORMAL,
                                                            gdk.RGBA(0, 0, 0, 1))

        else:
            buffer_label_to_appear = "00:00"
            self.label_control_current_time.override_color(gtk.StateFlags.NORMAL,
                                                           gdk.RGBA(0, 0, 0, 1))
            self.label_view_current_time.override_color(gtk.StateFlags.NORMAL,
                                                        gdk.RGBA(0, 0, 0, 1))
            # if a zero is detected at the board counter, the game can be stopped (if not already)
            # due to detection time which could be 0,1.. 0,9s then we add 0,5 sec (middle value)
            # and force the toggle button to stop
            if action_start_time_of_the_game_is_ACTIVE and watch_stop:
                time.sleep(0.5)
                action_start_time_of_the_game_is_ACTIVE = False

                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("*************** countdown activity ****************\n")
                    logfile_game_handler.write("  counter at zero / period end\n")

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "  counter at zero / period end\n")

                    logfile_game_handler.write("  at time     : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write(
                        "  blue team          : %s\n" % (str(self.entry_team_blue_name.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "  blue team          : %s\n" % (str(self.entry_team_blue_name.get_text())))

                    logfile_game_handler.write(
                        "  white team         : %s\n" % (str(self.entry_team_white_name.get_text())))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "  white team         : %s\n" % (str(self.entry_team_white_name.get_text())))

                    logfile_game_handler.write(
                        "  tournament         : %s\n" % (str(self.entry_tournament_name.get_text())))


                    if left_team_is_blue:
                        logfile_game_handler.write(
                            "points results blue: %s   white: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                       self.label_control_points_team_right.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                            "points results blue: %s   white: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                       self.label_control_points_team_right.get_text()))

                    else:
                        logfile_game_handler.write(
                            "points results white: %s   blue: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                       self.label_control_points_team_right.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                            "points results white: %s   blue: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                       self.label_control_points_team_right.get_text()))

                    if left_team_is_blue:
                        logfile_game_handler.write("timeout blue: %s   timeout white: %s\n" %
                                                   (str(int(self.spinbutton_timeout_left.get_value())),
                                                    str(int(self.spinbutton_timeout_right.get_value()))))

                    else:
                        logfile_game_handler.write("timeout white: %s   timeout blue: %s\n" %
                                                   (str(int(self.spinbutton_timeout_right.get_value())),
                                                    str(int(self.spinbutton_timeout_left.get_value()))))

                    logfile_game_handler.write("       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_1_left.get_text()),
                    self.label_control_time_penalty_player_1_left.get_text(),
                    str(self.entry_name_penalty_player_1_right.get_text()),
                    self.label_control_time_penalty_player_1_right.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_1_left.get_text()),
                    self.label_control_time_penalty_player_1_left.get_text(),
                    str(self.entry_name_penalty_player_1_right.get_text()),
                    self.label_control_time_penalty_player_1_right.get_text()))

                    logfile_game_handler.write("       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_2_left.get_text()),
                    self.label_control_time_penalty_player_2_left.get_text(),
                    str(self.entry_name_penalty_player_2_right.get_text()),
                    self.label_control_time_penalty_player_2_right.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_2_left.get_text()),
                    self.label_control_time_penalty_player_2_left.get_text(),
                    str(self.entry_name_penalty_player_2_right.get_text()),
                    self.label_control_time_penalty_player_2_right.get_text()))

                    logfile_game_handler.write("       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_3_left.get_text()),
                    self.label_control_time_penalty_player_3_left.get_text(),
                    str(self.entry_name_penalty_player_3_right.get_text()),
                    self.label_control_time_penalty_player_3_right.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_3_left.get_text()),
                    self.label_control_time_penalty_player_3_left.get_text(),
                    str(self.entry_name_penalty_player_3_right.get_text()),
                    self.label_control_time_penalty_player_3_right.get_text()))

                    logfile_game_handler.write("  period %s\n" % (str(int(self.spinbutton_period.get_value()))))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()

                self.togglebutton_start_stop_game.set_label('   START\nPLAY TIME')
                self.togglebutton_start_stop_game.set_active(False)

            elif action_start_time_of_the_game_is_ACTIVE and not watch_stop and running_penalty:
                self.togglebutton_start_stop_game.set_label('noSTOP')

            elif action_start_time_of_the_game_is_ACTIVE and not watch_stop and not running_penalty:
                action_start_time_of_the_game_is_ACTIVE = False


                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("*************** countdown activity ****************\n")
                    logfile_game_handler.write("counter at zero / period end\n")

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "counter at zero / period end\n")

                    logfile_game_handler.write("  at time     : %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write(
                        "  blue team          : %s\n" % (str(self.entry_team_blue_name.get_text())))

                    logfile_game_handler.write(
                        "  white team         : %s\n" % (str(self.entry_team_white_name.get_text())))

                    logfile_game_handler.write(
                        "  tournament         : %s\n" % (str(self.entry_tournament_name.get_text())))
                    if left_team_is_blue:
                        logfile_game_handler.write(
                            "points results blue: %s   white: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                       self.label_control_points_team_right.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                            "points results blue: %s   white: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                       self.label_control_points_team_right.get_text()))

                    else:
                        logfile_game_handler.write(
                            "points results white: %s   blue: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                       self.label_control_points_team_right.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                            "points results white: %s   blue: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                       self.label_control_points_team_right.get_text()))

                    if left_team_is_blue:
                        logfile_game_handler.write("timeout blue: %s   timeout white: %s\n" %
                                                   (str(int(self.spinbutton_timeout_left.get_value())),
                                                    str(int(self.spinbutton_timeout_right.get_value()))))

                    else:
                        logfile_game_handler.write("timeout white: %s   timeout blue: %s\n" %
                                                   (str(int(self.spinbutton_timeout_right.get_value())),
                                                    str(int(self.spinbutton_timeout_left.get_value()))))


                    logfile_game_handler.write("       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_1_left.get_text()),
                    self.label_control_time_penalty_player_1_left.get_text(),
                    str(self.entry_name_penalty_player_1_right.get_text()),
                    self.label_control_time_penalty_player_1_right.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_1_left.get_text()),
                    self.label_control_time_penalty_player_1_left.get_text(),
                    str(self.entry_name_penalty_player_1_right.get_text()),
                    self.label_control_time_penalty_player_1_right.get_text()))

                    logfile_game_handler.write("       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_2_left.get_text()),
                    self.label_control_time_penalty_player_2_left.get_text(),
                    str(self.entry_name_penalty_player_2_right.get_text()),
                    self.label_control_time_penalty_player_2_right.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_2_left.get_text()),
                    self.label_control_time_penalty_player_2_left.get_text(),
                    str(self.entry_name_penalty_player_2_right.get_text()),
                    self.label_control_time_penalty_player_2_right.get_text()))

                    logfile_game_handler.write("       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_3_left.get_text()),
                    self.label_control_time_penalty_player_3_left.get_text(),
                    str(self.entry_name_penalty_player_3_right.get_text()),
                    self.label_control_time_penalty_player_3_right.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "       %2s  %5s                      %2s %5s\n" % (
                    str(self.entry_name_penalty_player_3_left.get_text()),
                    self.label_control_time_penalty_player_3_left.get_text(),
                    str(self.entry_name_penalty_player_3_right.get_text()),
                    self.label_control_time_penalty_player_3_right.get_text()))

                    logfile_game_handler.write("  period %s\n" % (str(int(self.spinbutton_period.get_value()))))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()


                self.togglebutton_start_stop_game.set_label('   START\nPLAY TIME')
                self.togglebutton_start_stop_game.set_active(False)
        #
        self.label_control_current_time.set_text(buffer_label_to_appear)
        self.label_view_current_time.set_text(buffer_label_to_appear)
        #
        # update all timepenalty counter
        # LEFT
        if counter_seconds_time_penalty_player_1_left >= 0 and running_time_penalty_player_1_left:
            m, s = divmod(counter_seconds_time_penalty_player_1_left, 60)
            buffer_label_to_appear = "%02d:%02d" % (m, s)
            self.label_control_time_penalty_player_1_left.set_text(buffer_label_to_appear)

            if self.button_type_view_copycontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_1_left.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_1_right.set_text(buffer_label_to_appear)


            if counter_seconds_time_penalty_player_1_left <= warning_timepenalty:   # blinking of letters
                m, s = divmod(counter_seconds_time_penalty_player_1_left, 2)
                if s > 0:  # white letters
                    self.label_control_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 0.2))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))
                    else:
                        self.label_view_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))

                else:  # black letters
                    self.label_control_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    else:
                        self.label_view_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))


            #
        if counter_seconds_time_penalty_player_2_left >= 0 and running_time_penalty_player_2_left:
            m, s = divmod(counter_seconds_time_penalty_player_2_left, 60)
            buffer_label_to_appear = "%02d:%02d" % (m, s)
            self.label_control_time_penalty_player_2_left.set_text(buffer_label_to_appear)

            if self.button_type_view_copycontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_2_left.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_2_right.set_text(buffer_label_to_appear)

            if counter_seconds_time_penalty_player_2_left <= warning_timepenalty:   # blinking of letters
                m, s = divmod(counter_seconds_time_penalty_player_2_left, 2)
                if s > 0:  # white letters
                    self.label_control_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 0.2))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))
                    else:
                        self.label_view_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))

                else:  # black letters
                    self.label_control_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    else:
                        self.label_view_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))

            #
        if counter_seconds_time_penalty_player_3_left >= 0 and running_time_penalty_player_3_left:
            m, s = divmod(counter_seconds_time_penalty_player_3_left, 60)
            buffer_label_to_appear = "%02d:%02d" % (m, s)
            self.label_control_time_penalty_player_3_left.set_text(buffer_label_to_appear)

            if self.button_type_view_copycontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_3_left.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_3_right.set_text(buffer_label_to_appear)

            if counter_seconds_time_penalty_player_3_left <= warning_timepenalty:   # blinking of letters
                m, s = divmod(counter_seconds_time_penalty_player_3_left, 2)
                if s > 0:  # white letters
                    self.label_control_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 0.2))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))
                    else:
                        self.label_view_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))

                else:  # black letters
                    self.label_control_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    else:
                        self.label_view_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))

        #
        # update all timepenalty counter
        # RIGHT
        if counter_seconds_time_penalty_player_1_right >= 0 and running_time_penalty_player_1_right:
            m, s = divmod(counter_seconds_time_penalty_player_1_right, 60)
            buffer_label_to_appear = "%02d:%02d" % (m, s)
            self.label_control_time_penalty_player_1_right.set_text(buffer_label_to_appear)

            if self.button_type_view_copycontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_1_right.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_1_left.set_text(buffer_label_to_appear)
            #


            if counter_seconds_time_penalty_player_1_right <= warning_timepenalty:   # blinking of letters
                m, s = divmod(counter_seconds_time_penalty_player_1_right, 2)
                if s > 0:  # white letters
                    self.label_control_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 0.2))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))
                    else:
                        self.label_view_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))

                else:  # black letters
                    self.label_control_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    else:
                        self.label_view_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))



        if counter_seconds_time_penalty_player_2_right >= 0 and running_time_penalty_player_2_right:
            m, s = divmod(counter_seconds_time_penalty_player_2_right, 60)
            buffer_label_to_appear = "%02d:%02d" % (m, s)
            self.label_control_time_penalty_player_2_right.set_text(buffer_label_to_appear)
            #
            if self.button_type_view_copycontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_2_right.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_2_left.set_text(buffer_label_to_appear)
            #


            if counter_seconds_time_penalty_player_2_right <= warning_timepenalty:   # blinking of letters
                m, s = divmod(counter_seconds_time_penalty_player_2_right, 2)
                if s > 0:  # white letters
                    self.label_control_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 0.2))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))
                    else:
                        self.label_view_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 0, 0.2))

                else:  # black letters
                    self.label_control_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))
                    else:
                        self.label_view_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 0, 1))



        if counter_seconds_time_penalty_player_3_right >= 0 and running_time_penalty_player_3_right:
            m, s = divmod(counter_seconds_time_penalty_player_3_right, 60)
            buffer_label_to_appear = "%02d:%02d" % (m, s)
            self.label_control_time_penalty_player_3_right.set_text(buffer_label_to_appear)
            #
            if self.button_type_view_copycontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_3_right.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_3_left.set_text(buffer_label_to_appear)
            #

            if counter_seconds_time_penalty_player_3_right <= warning_timepenalty:  # blinking of letters
                m, s = divmod(counter_seconds_time_penalty_player_3_right, 2)
                if s > 0:  # white letters
                    self.label_control_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 0, 0.2))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(0, 0, 0, 0.2))
                    else:
                        self.label_view_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 0, 0.2))

                else:  # black letters
                    self.label_control_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 0, 1))
                    if self.button_type_view_copycontrolview.get_active() \
                            and self.button_separate_game_view_on.get_active():
                        self.label_view_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                               gdk.RGBA(0, 0, 0, 1))
                    else:
                        self.label_view_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                              gdk.RGBA(0, 0, 0, 1))


        # update time sequence counter
        #
        if running_penalty or running_timeout or running_break:
            if counter_seconds_special_time_sequence > 0:
        #        print("def update_timer_labels: counter_seconds_special_time_sequence is ",
        #              counter_seconds_special_time_sequence)
                m, s = divmod(counter_seconds_special_time_sequence, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
        #        print("buffer_label_to_appear ", buffer_label_to_appear)
                self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                self.label_view_special_time_sequence.set_text(buffer_label_to_appear)

                if (running_timeout or running_break) and counter_seconds_special_time_sequence < warning_break_timeout:
                    self.label_view_status_specific_timesequence.set_text("go to wall")

                if (running_timeout or running_break) and counter_seconds_special_time_sequence < warning_break_timeout and counter_seconds_special_time_sequence> 0:
                    m2, s2 = divmod(counter_seconds_special_time_sequence, 2)
                    if s2 > 0:  # white letters
                        self.label_control_special_time_sequence.override_color(gtk.StateFlags.NORMAL,
                                                                                      gdk.RGBA(0, 0, 0, 0.2))
                        if self.button_separate_game_view_on.get_active():
                            self.label_view_status_specific_timesequence.override_color(gtk.StateFlags.NORMAL,
                                                                                       gdk.RGBA(0, 0, 0, 0.2))

                    else:  # black letters
                        self.label_control_special_time_sequence.override_color(gtk.StateFlags.NORMAL,
                                                                                      gdk.RGBA(0, 0, 0, 1))
                        if self.button_separate_game_view_on.get_active():
                            self.label_view_status_specific_timesequence.override_color(gtk.StateFlags.NORMAL,
                                                                                       gdk.RGBA(0, 0, 0, 1))



            #                if self.button_stop_special_time_sequence.get_active():
            #                    self.label_view_status_specific_timesequence.set_text("stopped")
            #                stopped_special_time_sequence = True
            #            else:
            #                self.label_view_status_specific_timesequence.set_text("running")

            elif running_penalty and now_dont_stop:
                # case of the last penalty is still running when
                # the main watch was stopped

                if counter_seconds_special_time_sequence >= 0:
        #            print("def update_timer_labels: counter_seconds_special_time_sequence is ",
        #                  counter_seconds_special_time_sequence)
                    m, s = divmod(counter_seconds_special_time_sequence, 60)
                    buffer_label_to_appear = "%02d:%02d" % (m, s)
        #            print("buffer_label_to_appear ", buffer_label_to_appear)
                    self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                    self.label_view_special_time_sequence.set_text(buffer_label_to_appear)

            else:
                stopped_special_time_sequence = True
                counter_seconds_special_time_sequence = 0
                #                if self.button_special_time_sequence_none.get_active():
                #                    self.label_view_status_specific_timesequence.set_text("none")
                #                else:
                #                    self.label_view_status_specific_timesequence.set_text("ende")
                buffer_label_to_appear = "00:00"
                self.button_stop_special_time_sequence.set_active(True)  # activate the stop button
        #        print("buffer_label_to_appear ", buffer_label_to_appear)
                self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                self.label_view_special_time_sequence.set_text(buffer_label_to_appear)
                self.label_control_special_time_sequence.override_color(gtk.StateFlags.NORMAL,
                                                                        gdk.RGBA(0, 0, 0, 1))
                if self.button_separate_game_view_on.get_active():
                    self.label_view_status_specific_timesequence.override_color(gtk.StateFlags.NORMAL,
                                                                                gdk.RGBA(0, 0, 0, 1))
                running_penalty = False
                running_timeout = False
                running_break = False
                #
        #
        # update the other labels
        #
        diverse_numbers = int(self.spinbutton_points_team_left.get_value())
        if diverse_numbers > 9:
            buffer_label_to_appear = "%02d" % diverse_numbers
        else:
            buffer_label_to_appear = "%01d" % diverse_numbers
        #print("buffer_label_to_appear points left ", buffer_label_to_appear)
        self.label_control_points_team_left.set_text(buffer_label_to_appear)

        if self.button_type_view_copycontrolview.get_active() \
                and self.button_separate_game_view_on.get_active():
            self.label_view_points_team_left.set_text(buffer_label_to_appear)
        else:
            self.label_view_points_team_right.set_text(buffer_label_to_appear)
        #
        diverse_numbers = int(self.spinbutton_points_team_right.get_value())
        if diverse_numbers > 9:
            buffer_label_to_appear = "%02d" % diverse_numbers
        else:
            buffer_label_to_appear = "%01d" % diverse_numbers
        #print("Points right", buffer_label_to_appear)
        self.label_control_points_team_right.set_text(buffer_label_to_appear)
        #
        if self.button_type_view_copycontrolview.get_active() \
                and self.button_separate_game_view_on.get_active():
            self.label_view_points_team_right.set_text(buffer_label_to_appear)
        else:
            self.label_view_points_team_left.set_text(buffer_label_to_appear)
        #
        diverse_numbers = int(self.spinbutton_timeout_left.get_value())
        buffer_label_to_appear = "%01d" % diverse_numbers
        #print("Timeout_left ", buffer_label_to_appear)
        if self.button_type_view_copycontrolview.get_active() \
                and self.button_separate_game_view_on.get_active():
            self.label_view_timeout_left.set_text(buffer_label_to_appear)
        else:
            self.label_view_timeout_right.set_text(buffer_label_to_appear)
        #
        diverse_numbers = int(self.spinbutton_timeout_right.get_value())
        buffer_label_to_appear = "%01d" % diverse_numbers
        #print("Timeout_right ", buffer_label_to_appear)
        if self.button_type_view_copycontrolview.get_active() \
                and self.button_separate_game_view_on.get_active():
            self.label_view_timeout_right.set_text(buffer_label_to_appear)
        else:
            self.label_view_timeout_left.set_text(buffer_label_to_appear)
        #
        diverse_numbers = int(self.spinbutton_period.get_value())
        buffer_label_to_appear = "%01d" % diverse_numbers
        #print("Period ", buffer_label_to_appear)
        self.label_view_period.set_text(buffer_label_to_appear)
        #

    ############################################################################################
    #
    # control page
    #
    ############################################################################################
    #
    def start_stop_game(self, widget, data=None):

        global running_first_period_time
        global logfile_game
        global running_second_period_time
        global start_time_of_the_game
        global buffer_last_time_start
        global buffer_last_time_stop
        global buffer_last_started_ellapsed_period_time_seconds
        global break_mode
        global penalty_mode
        global timeout_mode
        global action_start_time_of_the_game_is_ACTIVE
        global game_started
        global counter_seconds_board
        global ellapsed_period_time_seconds
        global stopped_special_time_sequence
        global counter_seconds_special_time_sequence
        global add_time_seconds
        global period_time_in_second_orig
        global period_time_in_second
        global running_time_penalty_player_1_left
        global running_time_penalty_player_2_left
        global running_time_penalty_player_3_left
        global running_time_penalty_player_1_right
        global running_time_penalty_player_2_right
        global running_time_penalty_player_3_right
        global buffer_last_time_stop_of_the_timepenalty_player1_left
        global buffer_last_time_stop_of_the_timepenalty_player2_left
        global buffer_last_time_stop_of_the_timepenalty_player3_left
        global buffer_last_time_stop_of_the_timepenalty_player1_right
        global buffer_last_time_stop_of_the_timepenalty_player2_right
        global buffer_last_time_stop_of_the_timepenalty_player3_right
        global buffer_last_time_start_of_the_timepenalty_player1_left
        global buffer_last_time_start_of_the_timepenalty_player2_left
        global buffer_last_time_start_of_the_timepenalty_player3_left
        global buffer_last_time_start_of_the_timepenalty_player1_right
        global buffer_last_time_start_of_the_timepenalty_player2_right
        global buffer_last_time_start_of_the_timepenalty_player3_right
        global buffer_last_started_ellapsed_time_penalty_player_1_left_seconds
        global ellapsed_time_penalty_player_1_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_2_left_seconds
        global ellapsed_time_penalty_player_2_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_3_left_seconds
        global ellapsed_time_penalty_player_3_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_1_right_seconds
        global ellapsed_time_penalty_player_1_right_seconds
        global buffer_last_started_ellapsed_time_penalty_player_2_right_seconds
        global ellapsed_time_penalty_player_2_right_seconds
        global buffer_last_started_ellapsed_time_penalty_player_3_right_seconds
        global ellapsed_time_penalty_player_3_right_seconds

        '''toggle button for start/stop of the game
        this is activated by the START/STOP button of the GUI
        INPUT:
        - click on the start-stop button on the GUI
        - diverse global parameter
        - advise from the RUN thread if a stop can be done (no stopped watch clicked)
        OUTPUT:
        - parameter stopping or not the label update        
        actions...'''

        #
        #print("\n\n\n")
        #print("toggle button start / stop activated")

        #if action_start_time_of_the_game_is_ACTIVE:
        #    print("def start_stop_game: stop activated by clicking or it will be stopped if main counter = 0")
        #else:
        #    print("def start_stop_game: start activated by clicking or it will be not activ if main counter = 0")
        #print("\n\n\n")
        #
        # logic first second period time tbd (if necessary)
        #        print("running_first_period_time",running_first_period_time)
        #        print("running_second_period_time",running_second_period_time)
        #

        #        if stopped_special_time_sequence:  # then the game can start
        #
        if (not running_first_period_time) and (not running_second_period_time):
            #
            # first start at all
            #
            game_started = True
            action_start_time_of_the_game_is_ACTIVE = True
            start_time_of_the_game = datetime.now()
            buffer_last_time_start = datetime.now()
            buffer_last_started_ellapsed_period_time_seconds = 0
            stopped_special_time_sequence = True
            ellapsed_period_time_seconds = 0
            counter_seconds_special_time_sequence = 0
            running_first_period_time = True
            running_second_period_time = False

            self.save_setting_changes(self)    # activate the setting saving for the first start

            period_time_in_second = 60 * int(self.spinbutton_period_time.get_value())
            period_time_in_second_orig = 60 * int(self.spinbutton_period_time.get_value())

            counter_seconds_board = 60 * int(self.spinbutton_period_time.get_value())

            # put a new label status in order to announce the next possible action is to "STOP"
            self.togglebutton_start_stop_game.set_label('STOP Time')
        #    print("def start_stop_game: counter_seconds_board  ", counter_seconds_board)

            if not thread_time_control.is_alive():
        #        print("thread time control not alive -> will be started")
                thread_time_control.start()
                #
            #
            break_mode = False
            penalty_mode = False
            timeout_mode = False
            buffer_label_to_appear = "none"
            self.label_view_specific_timesequence.set_text(buffer_label_to_appear)
            self.label_view_status_specific_timesequence.set_text(buffer_label_to_appear)
            self.label_view_special_time_sequence.set_text(buffer_label_to_appear)
            #
            # update the view with tournament data
            self.label_control_tournament_name.set_text(self.entry_tournament_name.get_text())
            self.label_control_tournament_contact.set_text(self.entry_tournament_contact.get_text())
            self.label_view_tournament_name.set_text(self.entry_tournament_name.get_text())
            self.label_view_tournament_contact.set_text(self.entry_tournament_contact.get_text())
            #
            if left_team_is_blue:
                self.label_control_team_name_left.set_text(self.entry_team_blue_name.get_text())
                self.label_control_team_name_right.set_text(self.entry_team_white_name.get_text())
                if self.button_type_view_copycontrolview.get_active():
                    self.label_view_team_name_left.set_text(self.entry_team_blue_name.get_text())
                    self.label_view_team_name_right.set_text(self.entry_team_white_name.get_text())
                else:
                    self.label_view_team_name_right.set_text(self.entry_team_blue_name.get_text())
                    self.label_view_team_name_left.set_text(self.entry_team_white_name.get_text())
            else:
                self.label_control_team_name_left.set_text(self.entry_team_white_name.get_text())
                self.label_control_team_name_right.set_text(self.entry_team_blue_name.get_text())
                if self.button_type_view_copycontrolview.get_active():
                    self.label_view_team_name_left.set_text(self.entry_team_white_name.get_text())
                    self.label_view_team_name_right.set_text(self.entry_team_blue_name.get_text())
                else:
                    self.label_view_team_name_right.set_text(self.entry_team_white_name.get_text())
                    self.label_view_team_name_left.set_text(self.entry_team_blue_name.get_text())
            #
            # no running countdown of players because the game just started and a new game dont start (usually)
            # with a timepenalty of a player
            # if such case is possible, the logic of this application must be adapted
            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                logfile_game_handler.write("************* control board activity **************\n")
                logfile_game_handler.write("START GAME \n")

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "START GAME \n")

                logfile_game_handler.write(
                    "  start time of the game        : %s h:min:s\n\n" % (str(start_time_of_the_game.strftime("%H:%M:%S"))))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                    "  start time of the game        : %s h:min:s\n\n" % (str(start_time_of_the_game.strftime("%H:%M:%S"))))

                #logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()

                self.log_setting_changes(self)

                #logfile_game_handler.write("  start time         : %s\n" % (str(start_time_of_the_game.strftime("%H:%M:%S"))))
                #logfile_game_handler.write("  timepenalty        : %s\n" % (str(timepenalty_maximum_seconds)))
                #logfile_game_handler.write("  penalty            : %s\n" % (str(penalty_maximum_seconds)))
                #logfile_game_handler.write("  timeout            : %s\n" % (str(timeout_maximum_seconds)))
                #logfile_game_handler.write("  break              : %s\n" % (str(break_maximum_seconds)))
                #logfile_game_handler.write(
                #    "  blue team          : %s\n" % (str(self.entry_team_blue_name.get_text())))
                #logfile_game_handler.write(
                #    "  white team         : %s\n" % (str(self.entry_team_white_name.get_text())))
                #logfile_game_handler.write(
                #    "  tournament         : %s\n" % (str(self.entry_tournament_name.get_text())))
                #logfile_game_handler.write(
                #    "  tournament contact : %s\n" % (str(self.entry_tournament_contact.get_text())))
                #logfile_game_handler.write(
                #    "  warning timepenalty: %s\n" % (str(int(self.spinbutton_warning_timepenalty.get_value()))))
                #logfile_game_handler.write(
                #    "  stop watch         : %s\n" % (str(self.button_stop_watch.get_active())))
                #logfile_game_handler.write(
                #    "  (add time          : %s)\n" % (str(int(self.spinbutton_add_time.get_value()))))
                logfile_game_handler = open(logfile_game, 'a')
                #logfile_game_handler.write("************* control board activity **************\n")
                #logfile_game_handler.write("START GAME board data\n")
                #logfile_game_handler.write("***************************************************\n")
                if left_team_is_blue:
                    logfile_game_handler.write(
                        "points results blue: %s   white: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                   self.label_control_points_team_right.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                        "points results blue: %s   white: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                   self.label_control_points_team_right.get_text()))

                else:
                    logfile_game_handler.write(
                        "points results white: %s   blue: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                   self.label_control_points_team_right.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                        "points results white: %s   blue: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                   self.label_control_points_team_right.get_text()))

                if left_team_is_blue:
                    logfile_game_handler.write("timeout blue: %s   timeout white: %s\n" %
                                               (str(int(self.spinbutton_timeout_left.get_value())),
                                                str(int(self.spinbutton_timeout_right.get_value()))))

                else:
                    logfile_game_handler.write("timeout white: %s   timeout blue: %s\n" %
                                               (str(int(self.spinbutton_timeout_right.get_value())),
                                                str(int(self.spinbutton_timeout_left.get_value()))))

                logfile_game_handler.write(
                    "period:     %s\n" % (str(int(self.spinbutton_period.get_value()))))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()
            #
        else:
            #
            # time countdown is running (or not = stay at 0) and start OR stop clicked
            #
            if action_start_time_of_the_game_is_ACTIVE:

                if not watch_stop and ((ellapsed_time_game_in_seconds - ellapsed_period_time_seconds) >= add_time_seconds):
                    # if nostop watch; stop button become inactive
                    # counter_seconds_board!=period_time_in_second for the clock not to run when the time reset is activated


        #                print("*************************************")
        #                print("ellapsed_time_game_in_seconds", ellapsed_time_game_in_seconds)
        #                print("ellapsed_period_time_seconds", ellapsed_period_time_seconds)
        #                print("*************************************")

                        #counter_seconds_board != period_time_in_second:
                        self.togglebutton_start_stop_game.set_label('noSTOP')
                        self.togglebutton_start_stop_game.set_active(False)
                        # dont do anything. the game must run and the start stop button must become inactiv

                else:

                    action_start_time_of_the_game_is_ACTIVE = False
                    #
                    # perhaps it would be better to check if the a first period was started (a second not important)
                    running_first_period_time = True
                    running_second_period_time = False
                    #
        #            print("def start_stop_game: STOP at counter_seconds_board  ", counter_seconds_board)

                    if counter_seconds_board > 0:  # in case the countdown was running it means was not already at zero
                        self.togglebutton_start_stop_game.set_label('START Time')
                        buffer_last_time_stop = datetime.now()
                        #
                        buffer_last_time_stop_of_the_timepenalty_player1_left = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player2_left = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player3_left = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player1_right = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player2_right = datetime.now()
                        buffer_last_time_stop_of_the_timepenalty_player3_right = datetime.now()
                        #
                        buffer_label_to_appear = "none"
                        self.label_view_specific_timesequence.set_text(buffer_label_to_appear)
                        self.label_view_status_specific_timesequence.set_text(buffer_label_to_appear)
                        buffer_label_to_appear = "00:00"
                        self.label_view_special_time_sequence.set_text(buffer_label_to_appear)
                        self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                        #
                        if self.button_log_functionality_on.get_active():
                            self.label_log_dialog_time.set_text(self.label_control_current_time.get_text())

                            logfile_game_handler = open(logfile_game, 'a')
                            logfile_game_handler.write    ("************* control board activity **************\n")
                            logfile_game_handler.write    ("STOP \n")

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                  "STOP \n")

                            logfile_game_handler.write    ("  at time                : %s h:min:s\n" % (str(buffer_last_time_stop.strftime("%H:%M:%S"))))
                            logfile_game_handler.write    ("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                            logfile_game_handler.write    ("  blue team              : %s\n" % (str(self.entry_team_blue_name.get_text())))
                            logfile_game_handler.write    ("  white team             : %s\n" % (str(self.entry_team_white_name.get_text())))
                            logfile_game_handler.write    ("  tournament             : %s\n" % (str(self.entry_tournament_name.get_text())))
                            if left_team_is_blue:
                                logfile_game_handler.write("  points status   blue:  %2s   white: %2s\n" % (self.label_control_points_team_left.get_text(),
                                                                self.label_control_points_team_right.get_text()))

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                           "  points status   blue:  %2s   white: %2s\n" % (self.label_control_points_team_left.get_text(),
                                                                self.label_control_points_team_right.get_text()))

                            else:
                                logfile_game_handler.write("  points status   white: %2s   blue:  %2s\n" % (self.label_control_points_team_left.get_text(),
                                                                self.label_control_points_team_right.get_text()))

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                           "  points status   white: %2s   blue:  %2s\n" % (self.label_control_points_team_left.get_text(),
                                                                self.label_control_points_team_right.get_text()))

                            if left_team_is_blue:
                                logfile_game_handler.write("  timeout         blue:  %s    white: %s\n" %
                                                           (str(int(self.spinbutton_timeout_left.get_value())),
                                                            str(int(self.spinbutton_timeout_right.get_value()))))

                                logfile_game_handler.write("  timepenalty blue                timepenalty white\n")

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                           "  timepenalty blue                timepenalty white\n")

                            else:
                                logfile_game_handler.write("  timeout         white: %s    blue : %s\n" %
                                                           (str(int(self.spinbutton_timeout_right.get_value())),
                                                            str(int(self.spinbutton_timeout_left.get_value()))))

                                logfile_game_handler.write("  timepenalty white               timepenalty blue\n")

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                        "  timepenalty white               timepenalty blue\n")


                            logfile_game_handler.write    ("    %2s  %5s min:s                   %2s %5s min:s\n" %
                                                           (str(self.entry_name_penalty_player_1_left.get_text()),
                                                            self.label_control_time_penalty_player_1_left.get_text(),
                                                            str(self.entry_name_penalty_player_1_right.get_text()),
                                                            self.label_control_time_penalty_player_1_right.get_text()))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                           "    %2s  %5s min:s                   %2s %5s min:s\n" %
                                                           (str(self.entry_name_penalty_player_1_left.get_text()),
                                                            self.label_control_time_penalty_player_1_left.get_text(),
                                                            str(self.entry_name_penalty_player_1_right.get_text()),
                                                            self.label_control_time_penalty_player_1_right.get_text()))

                            logfile_game_handler.write    ("    %2s  %5s min:s                   %2s %5s min:s\n" %
                                                           (str(self.entry_name_penalty_player_2_left.get_text()),
                                                            self.label_control_time_penalty_player_2_left.get_text(),
                                                            str(self.entry_name_penalty_player_2_right.get_text()),
                                                            self.label_control_time_penalty_player_2_right.get_text()))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                        "    %2s  %5s min:s                   %2s %5s min:s\n" %
                                                           (str(self.entry_name_penalty_player_2_left.get_text()),
                                                            self.label_control_time_penalty_player_2_left.get_text(),
                                                            str(self.entry_name_penalty_player_2_right.get_text()),
                                                            self.label_control_time_penalty_player_2_right.get_text()))

                            logfile_game_handler.write    ("    %2s  %5s min:s                   %2s %5s min:s\n" %
                                                           (str(self.entry_name_penalty_player_3_left.get_text()),
                                                            self.label_control_time_penalty_player_3_left.get_text(),
                                                            str(self.entry_name_penalty_player_3_right.get_text()),
                                                            self.label_control_time_penalty_player_3_right.get_text()))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "    %2s  %5s min:s                   %2s %5s min:s\n" %
                                                           (str(self.entry_name_penalty_player_3_left.get_text()),
                                                            self.label_control_time_penalty_player_3_left.get_text(),
                                                            str(self.entry_name_penalty_player_3_right.get_text()),
                                                            self.label_control_time_penalty_player_3_right.get_text()))

                            logfile_game_handler.write    ("  period %s\n" % (str(int(self.spinbutton_period.get_value()))))

                            logfile_game_handler.write("***************************************************\n")
                            logfile_game_handler.close()


                            ####################################
                            # clean the log window entries before the window opens
                            #
                            for i in range(10):
                                for j in range(14):
                                    if j == 0:
                                        self.entry_logarray[i][j].set_active(False)
                                    elif j == 1:
                                        self.entry_logarray[i][j].set_active(False)
                                    elif j == 2 or j == 13:
                                        self.entry_logarray[i][j].set_text("")
                                    else:
                                        self.entry_logarray[i][j].set_active(False)

                            self.entry_log_dialog_remark_referee.set_text("")
                            self.entry_log_dialog_remark_scripter.set_text("")
                            ####################################

                            self.logdialog.show()

                    else:
                        # second counter is at zero; only possibility is to restart a play time. And the button is inactive.
                        # as long the counter is not resetted to 15min for example
                        self.togglebutton_start_stop_game.set_label('   START\nPLAY TIME')
                        self.togglebutton_start_stop_game.set_active(False)
                        if self.button_log_functionality_on.get_active():
                            now = datetime.now()
                            logfile_game_handler = open(logfile_game, 'a')
                            logfile_game_handler.write    ("***************************************************\n")
                            logfile_game_handler.write    ("STOP; COUNTDOWN AT ZERO = END OF PERIOD; SUMMARY\n")

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                        "STOP; COUNTDOWN AT ZERO = END OF PERIOD; SUMMARY\n")

                            logfile_game_handler.write    ("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                        "  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                            logfile_game_handler.write    ("  period time         : %s s\n" % (str(period_time_in_second)))
                            logfile_game_handler.write    ("  timepenalty         : %s s\n" % (str(timepenalty_maximum_seconds)))
                            logfile_game_handler.write    ("  penalty             : %s s\n" % (str(penalty_maximum_seconds)))
                            logfile_game_handler.write    ("  timeout             : %s s\n" % (str(timeout_maximum_seconds)))
                            logfile_game_handler.write    ("  break               : %s s\n" % (str(break_maximum_seconds)))
                            logfile_game_handler.write    ("  blue team           : %s\n" % (str(self.entry_team_blue_name.get_text())))
                            logfile_game_handler.write    ("  white team          : %s\n" % (str(self.entry_team_white_name.get_text())))
                            logfile_game_handler.write    ("  tournament          : %s\n" % (str(self.entry_tournament_name.get_text())))
                            logfile_game_handler.write    ("  tournament contact  : %s\n" % (str(self.entry_tournament_contact.get_text())))
                            logfile_game_handler.write    ("  warning timepenalty : %s\n" % (str(int(self.spinbutton_warning_timepenalty.get_value()))))
                            logfile_game_handler.write    ("  stop watch          : %s\n" % (str(self.button_stop_watch.get_active())))
                            logfile_game_handler.write    ("  (add time           : %s min)\n\n" % (str(int(self.spinbutton_add_time.get_value()))))
                            logfile_game_handler.write(
                                "  period:  %s\n" % (str(int(self.spinbutton_period.get_value()))))
                            if left_team_is_blue:
                                logfile_game_handler.write("  points results blue : %s    white: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                self.label_control_points_team_right.get_text()))

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                            "  points results blue : %s    white: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                self.label_control_points_team_right.get_text()))


                            else:
                                logfile_game_handler.write("  points results white: %s   blue: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                self.label_control_points_team_right.get_text()))

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                            "  points results white: %s   blue: %s\n" % (self.label_control_points_team_left.get_text(),
                                                                self.label_control_points_team_right.get_text()))

                            if left_team_is_blue:
                                logfile_game_handler.write("  timeout blue: %s    timeout white: %s\n" %
                                                           (str(int(self.spinbutton_timeout_left.get_value())),
                                                            str(int(self.spinbutton_timeout_right.get_value()))))

                                logfile_game_handler.write("  timepenalty blue                timepenalty white:\n")

                            else:
                                logfile_game_handler.write("  timeout white: %s    timeout blue: %s\n" %
                                                           (str(int(self.spinbutton_timeout_right.get_value())),
                                                            str(int(self.spinbutton_timeout_left.get_value()))))

                                logfile_game_handler.write("  timepenalty white               timepenalty blue:\n")

                            logfile_game_handler.write    ("       %2s  %5s min:s                %2s %5s min:s\n" % (str(self.entry_name_penalty_player_1_left.get_text()),self.label_control_time_penalty_player_1_left.get_text(),str(self.entry_name_penalty_player_1_right.get_text()),self.label_control_time_penalty_player_1_right.get_text()))
                            logfile_game_handler.write    ("       %2s  %5s min:s                %2s %5s min:s\n" % (str(self.entry_name_penalty_player_2_left.get_text()),self.label_control_time_penalty_player_2_left.get_text(),str(self.entry_name_penalty_player_2_right.get_text()),self.label_control_time_penalty_player_2_right.get_text()))
                            logfile_game_handler.write    ("       %2s  %5s min:s                %2s %5s min:s\n" % (str(self.entry_name_penalty_player_3_left.get_text()),self.label_control_time_penalty_player_3_left.get_text(),str(self.entry_name_penalty_player_3_right.get_text()),self.label_control_time_penalty_player_3_right.get_text()))
                            logfile_game_handler.write("***************************************************\n")
                            logfile_game_handler.close()

                #
            else:
                # the time was stopped, so now, it can restart ONLY if the counter seconds is >0
                # counter penalty / timeout / break to none when the game is re-started
                #
                if counter_seconds_board > 0:

                    now = datetime.now()
                    if self.button_log_functionality_on.get_active():
                        logfile_game_handler = open(logfile_game, 'a')
                        logfile_game_handler.write("************* control board activity **************\n")
                        logfile_game_handler.write("START \n")

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "START \n")

                        logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                        logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                        if left_team_is_blue:
                            logfile_game_handler.write("  points results blue : %s    white: %s\n" % (
                                        self.label_control_points_team_left.get_text(),
                                        self.label_control_points_team_right.get_text()))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "  points results blue : %s    white: %s\n" % (
                                        self.label_control_points_team_left.get_text(),
                                        self.label_control_points_team_right.get_text()))

                        else:
                            logfile_game_handler.write("  points results white: %s   blue: %s\n" % (
                                        self.label_control_points_team_left.get_text(),
                                        self.label_control_points_team_right.get_text()))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "  points results white: %s   blue: %s\n" % (
                                        self.label_control_points_team_left.get_text(),
                                        self.label_control_points_team_right.get_text()))

                        if left_team_is_blue:
                            logfile_game_handler.write("  timeout blue: %s    timeout white: %s\n" %
                                                       (str(int(self.spinbutton_timeout_left.get_value())),
                                                        str(int(self.spinbutton_timeout_right.get_value()))))

                            logfile_game_handler.write("  timepenalty blue                timepenalty white\n")

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                     "  timepenalty blue                timepenalty white\n")
                        else:
                            logfile_game_handler.write("  timeout white: %s    timeout blue: %s\n" %
                                                       (str(int(self.spinbutton_timeout_right.get_value())),
                                                        str(int(self.spinbutton_timeout_left.get_value()))))

                            logfile_game_handler.write("  timepenalty white               timepenalty blue\n")

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                       "  timepenalty white               timepenalty blue\n")


                        logfile_game_handler.write("    %2s  %5s min:s                   %2s %5s min:s\n" % (
                        str(self.entry_name_penalty_player_1_left.get_text()),
                        self.label_control_time_penalty_player_1_left.get_text(),
                        str(self.entry_name_penalty_player_1_right.get_text()),
                        self.label_control_time_penalty_player_1_right.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                   "    %2s  %5s min:s                   %2s %5s min:s\n" % (
                        str(self.entry_name_penalty_player_1_left.get_text()),
                        self.label_control_time_penalty_player_1_left.get_text(),
                        str(self.entry_name_penalty_player_1_right.get_text()),
                        self.label_control_time_penalty_player_1_right.get_text()))

                        logfile_game_handler.write("    %2s  %5s min:s                   %2s %5s min:s\n" % (
                        str(self.entry_name_penalty_player_2_left.get_text()),
                        self.label_control_time_penalty_player_2_left.get_text(),
                        str(self.entry_name_penalty_player_2_right.get_text()),
                        self.label_control_time_penalty_player_2_right.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "    %2s  %5s min:s                   %2s %5s min:s\n" % (
                        str(self.entry_name_penalty_player_2_left.get_text()),
                        self.label_control_time_penalty_player_2_left.get_text(),
                        str(self.entry_name_penalty_player_2_right.get_text()),
                        self.label_control_time_penalty_player_2_right.get_text()))

                        logfile_game_handler.write("    %2s  %5s min:s                   %2s %5s min:s\n" % (
                        str(self.entry_name_penalty_player_3_left.get_text()),
                        self.label_control_time_penalty_player_3_left.get_text(),
                        str(self.entry_name_penalty_player_3_right.get_text()),
                        self.label_control_time_penalty_player_3_right.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "    %2s  %5s min:s                   %2s %5s min:s\n" % (
                        str(self.entry_name_penalty_player_3_left.get_text()),
                        self.label_control_time_penalty_player_3_left.get_text(),
                        str(self.entry_name_penalty_player_3_right.get_text()),
                        self.label_control_time_penalty_player_3_right.get_text()))

                        logfile_game_handler.write("***************************************************\n")
                        logfile_game_handler.close()


                    counter_seconds_special_time_sequence = 0
                    break_mode = False
                    penalty_mode = False
                    timeout_mode = False
                    self.button_special_time_sequence_none.set_active(True)
                    self.button_stop_special_time_sequence.set_active(True)
                    buffer_label_to_appear = "none"
                    self.label_view_specific_timesequence.set_text(buffer_label_to_appear)
                    self.label_view_status_specific_timesequence.set_text(buffer_label_to_appear)
                    #                buffer_label_to_appear = "00:00"
                    self.label_view_special_time_sequence.set_text(buffer_label_to_appear)
                    self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                    #
                    action_start_time_of_the_game_is_ACTIVE = True
                    self.togglebutton_start_stop_game.set_label('STOP Time')
        #            print("def start_stop_game: counter_seconds_board  ", counter_seconds_board)
                    buffer_last_time_start = datetime.now()
                    buffer_last_started_ellapsed_period_time_seconds = ellapsed_period_time_seconds
                    #
                    buffer_last_time_start_of_the_timepenalty_player1_left = datetime.now()
                    buffer_last_time_start_of_the_timepenalty_player2_left = datetime.now()
                    buffer_last_time_start_of_the_timepenalty_player3_left = datetime.now()
                    buffer_last_time_start_of_the_timepenalty_player1_right = datetime.now()
                    buffer_last_time_start_of_the_timepenalty_player2_right = datetime.now()
                    buffer_last_time_start_of_the_timepenalty_player3_right = datetime.now()
                    #
                    buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = \
                        ellapsed_time_penalty_player_1_left_seconds
                    buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = \
                        ellapsed_time_penalty_player_2_left_seconds
                    buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = \
                        ellapsed_time_penalty_player_3_left_seconds
                    buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = \
                        ellapsed_time_penalty_player_1_right_seconds
                    buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = \
                        ellapsed_time_penalty_player_2_right_seconds
                    buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = \
                        ellapsed_time_penalty_player_3_right_seconds
                    #
                    #
                else:
                    #now = datetime.now()
                    self.togglebutton_start_stop_game.set_active(False) # in order to avoid the start button to become
                    # grey when clicked and it is already stopped and at zero
                    action_start_time_of_the_game_is_ACTIVE = False


    def clear_reset_current_time(self, widget, data=None):
        global action_start_time_of_the_game_is_ACTIVE
        global game_started
        global logfile_game
        global start_time_of_the_game
        global buffer_last_time_start
        global period_time_in_second
        global buffer_last_time_stop
        global ellapsed_period_time_seconds
        global buffer_last_started_ellapsed_period_time_seconds
        global running_first_period_time
        global running_second_period_time
        #
        '''stop and reset time to the setting period value'''
        #
        # time reset only when game is started but currently not active
        # game will re-start from this time with the already stored duration
        #print("*******************************************************")
        #print("**                                                   **")
        #print("**  stop and reset time to the setting period value  **")
        #print("**                                                   **")
        #print("*******************************************************")

        if not action_start_time_of_the_game_is_ACTIVE and game_started:
            start_time_of_the_game = datetime.now()
            buffer_last_time_start = datetime.now()
            buffer_last_time_stop = datetime.now()

            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                logfile_game_handler.write("clear/reset game time to default\n")

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "clear/reset game time to default\n")

                logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()

            #
            buffer_last_started_ellapsed_period_time_seconds = 0
            ellapsed_period_time_seconds = 0
            #
            running_first_period_time = True  # from true to false for overtaking control of non stopped games
            running_second_period_time = False
            #
            period_time_in_second = 60 * int(self.spinbutton_period_time.get_value())
            counter_seconds_board = 60 * int(self.spinbutton_period_time.get_value())
        #    print("def update_timer_labels: counter_seconds_board is ", counter_seconds_board)
            m, s = divmod(counter_seconds_board, 60)  #
            buffer_label_to_appear = "%02d:%02d" % (m, s)
        #    print("buffer_label_to_appear ", buffer_label_to_appear)
            self.label_control_current_time.set_text(buffer_label_to_appear)

    def enter_time_correction(self, widget, data=None):
        # time correction only when game is not active
        # game will continue from this time
        # the already played time is not modified. it means buffer_last_started_ellapsed_period_time_seconds stay
        # .. logic to be developped later why this function
        # .. mean a new time shorter than the elapsed time cannot be uploaded
        #
        global action_start_time_of_the_game_is_ACTIVE
        global game_started
        global period_time_in_second
        global start_time_of_the_game
        global buffer_last_started_ellapsed_period_time_seconds  # not modified = elapsed time not reduced
        global ellapsed_period_time_seconds
        global running_first_period_time
        global running_second_period_time
        global counter_seconds_board
        global buffer_last_time_start
        global buffer_last_time_stop
        #
        # time correction only when you have started the game
        # else go to settings and change them
        if not action_start_time_of_the_game_is_ACTIVE and game_started:
        #    print("enter corrected time when confirmed")


            tempdata = ellapsed_period_time_seconds
            start_time_of_the_game = datetime.now()
            buffer_last_time_start = datetime.now()
            buffer_last_time_stop = datetime.now()
            #ellapsed_period_time_seconds = 0
            running_first_period_time = True
            running_second_period_time = False
            #
            resttime = 60 * int(self.spinbutton_minutes_time_correction.get_value()) + \
                                    int(self.spinbutton_seconds_time_correction.get_value())

            # added Aug7: adjust the new rest play time and take care of the existing time which exists
            # counter_seconds_board go automatic via run to resttime?
            buffer_last_started_ellapsed_period_time_seconds = 0
            period_time_in_second = tempdata + resttime
            counter_seconds_board = resttime

        #    print("def update_timer_labels: counter_seconds_board new is ", counter_seconds_board)
            m, s = divmod(counter_seconds_board, 60)
            buffer_label_to_appear = "%02d:%02d" % (m, s)
        #    print("buffer_label_to_appear ", buffer_label_to_appear)
            self.label_control_current_time.set_text(buffer_label_to_appear)

            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                logfile_game_handler.write("new time introduced\n")

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "new time introduced\n")

                logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                logfile_game_handler.write("  rest time new: %s s\n" % (str(resttime)))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "  rest time new: %s s\n" % (str(resttime)))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()

    #
    def switch_scoreboard_team_status(self, widget, data=None):
        global left_team_is_blue
        global team_name_left
        global team_name_right
        global action_start_time_of_the_game_is_ACTIVE
        global running_time_penalty_player_1_left
        global running_time_penalty_player_2_left
        global running_time_penalty_player_3_left
        global running_time_penalty_player_1_right
        global running_time_penalty_player_2_right
        global running_time_penalty_player_3_right
        global time_penalty_player_1_left_initialized
        global time_penalty_player_2_left_initialized
        global time_penalty_player_3_left_initialized
        global time_penalty_player_1_right_initialized
        global time_penalty_player_2_right_initialized
        global time_penalty_player_3_right_initialized

        global buffer_last_started_ellapsed_time_penalty_player_1_left_seconds
        global counter_seconds_time_penalty_player_1_left
        global ellapsed_time_penalty_player_1_left_seconds
        global buffer_last_time_start_of_the_timepenalty_player1_left

        global buffer_last_started_ellapsed_time_penalty_player_2_left_seconds
        global counter_seconds_time_penalty_player_2_left
        global ellapsed_time_penalty_player_2_left_seconds
        global buffer_last_time_start_of_the_timepenalty_player2_left

        global buffer_last_started_ellapsed_time_penalty_player_3_left_seconds
        global counter_seconds_time_penalty_player_3_left
        global ellapsed_time_penalty_player_3_left_seconds
        global buffer_last_time_start_of_the_timepenalty_player3_left

        global buffer_last_started_ellapsed_time_penalty_player_1_right_seconds
        global counter_seconds_time_penalty_player_1_right
        global ellapsed_time_penalty_player_1_right_seconds
        global buffer_last_time_start_of_the_timepenalty_player1_right

        global buffer_last_started_ellapsed_time_penalty_player_2_right_seconds
        global counter_seconds_time_penalty_player_2_right
        global ellapsed_time_penalty_player_2_right_seconds
        global buffer_last_time_start_of_the_timepenalty_player2_right

        global buffer_last_started_ellapsed_time_penalty_player_3_right_seconds
        global counter_seconds_time_penalty_player_3_right
        global ellapsed_time_penalty_player_3_right_seconds
        global buffer_last_time_start_of_the_timepenalty_player3_right

        global period_time_in_second
        global logfile_game
        global logfile_game_handler

        '''swap all data from the scoreboard team: penalty and score and color from left to right
        timepenalty player which are at 0 time will be cleared
        timeout number will be set to zero in case the period was at the end or the next period did not start
        all status of valid timepenalties will be exchanged from left to right'''

        #print("   ")
        #print("swap all data from the scoreboard team: penalty and score and color from left to right")
        #print("   ")
        #
        # swap when countdown is paused
        if not action_start_time_of_the_game_is_ACTIVE:

        ## swap timepenalty status, time and names only when time =0 or time = completed
        #if counter_seconds_board == 0 or ellapsed_period_time_seconds == 0 or \
        #        counter_seconds_board == period_time_in_second or \
        #        buffer_last_started_ellapsed_period_time_seconds == period_time_in_second:

            if counter_seconds_board == 0 or ellapsed_period_time_seconds == 0 or \
                          counter_seconds_board == period_time_in_second or \
                     buffer_last_started_ellapsed_period_time_seconds == period_time_in_second:
                self.spinbutton_timeout_left.set_value(0)
                self.spinbutton_timeout_right.set_value(0)
            #
            #
            if self.button_log_functionality_on.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                now = datetime.now()
                logfile_game_handler.write("************* control board activity **************\n")
                logfile_game_handler.write("switch board data\n")

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "switch board data\n")

                logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                if left_team_is_blue:
                    logfile_game_handler.write("  team blue (left) change to right side\n")

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "  team blue (left) change to right side\n")

                else:
                    logfile_game_handler.write("  team blue (right) change to left side\n")

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "  team blue (right) change to left side\n")

                logfile_game_handler.write("  all timepenalty player will be cleared\n  and only the active re-activated\n")
                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()


            # cap number 1..99 for control board to be switched.

            buffer_entry_name_penalty_player_1 = str(self.entry_name_penalty_player_1_left.get_text())
            buffer_entry_name_penalty_player_2 = str(self.entry_name_penalty_player_2_left.get_text())
            buffer_entry_name_penalty_player_3 = str(self.entry_name_penalty_player_3_left.get_text())
            #
            self.entry_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_right.get_text())
            self.entry_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_right.get_text())
            self.entry_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_right.get_text())
            self.entry_name_penalty_player_1_right.set_text(buffer_entry_name_penalty_player_1)
            self.entry_name_penalty_player_2_right.set_text(buffer_entry_name_penalty_player_2)
            self.entry_name_penalty_player_3_right.set_text(buffer_entry_name_penalty_player_3)
            #
            # all cap number transfered to the view board
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_right.get_text())
                self.label_view_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_right.get_text())
                self.label_view_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_right.get_text())
                self.label_view_name_penalty_player_1_right.set_text(self.entry_name_penalty_player_1_left.get_text())
                self.label_view_name_penalty_player_2_right.set_text(self.entry_name_penalty_player_2_left.get_text())
                self.label_view_name_penalty_player_3_right.set_text(self.entry_name_penalty_player_3_left.get_text())
            else:
                self.label_view_name_penalty_player_1_left.set_text(self.entry_name_penalty_player_1_left.get_text())
                self.label_view_name_penalty_player_2_left.set_text(self.entry_name_penalty_player_2_left.get_text())
                self.label_view_name_penalty_player_3_left.set_text(self.entry_name_penalty_player_3_left.get_text())
                self.label_view_name_penalty_player_1_right.set_text(self.entry_name_penalty_player_1_right.get_text())
                self.label_view_name_penalty_player_2_right.set_text(self.entry_name_penalty_player_2_right.get_text())
                self.label_view_name_penalty_player_3_right.set_text(self.entry_name_penalty_player_3_right.get_text())
            #
            # all timers are switched. Due to thread for updating the timing label, its perhaps enough to switch that
            # parameters
            # save the timepenalty status for recovering later after the activate / clear button are set

            buffer_counter_seconds_time_penalty_player_1_right = counter_seconds_time_penalty_player_1_left
            buffer_counter_seconds_time_penalty_player_2_right = counter_seconds_time_penalty_player_2_left
            buffer_counter_seconds_time_penalty_player_3_right = counter_seconds_time_penalty_player_3_left
            buffer_counter_seconds_time_penalty_player_1_left = counter_seconds_time_penalty_player_1_right
            buffer_counter_seconds_time_penalty_player_2_left = counter_seconds_time_penalty_player_2_right
            buffer_counter_seconds_time_penalty_player_3_left = counter_seconds_time_penalty_player_3_right
            #counter_seconds_time_penalty_player_1_right = buffer_counter_seconds_time_penalty_player_1
            #counter_seconds_time_penalty_player_2_right = buffer_counter_seconds_time_penalty_player_2
            #counter_seconds_time_penalty_player_3_right = buffer_counter_seconds_time_penalty_player_3
            #
            buffer_ellapsed_time_penalty_player_1_left_seconds = ellapsed_time_penalty_player_1_right_seconds
            buffer_ellapsed_time_penalty_player_2_left_seconds = ellapsed_time_penalty_player_2_right_seconds
            buffer_ellapsed_time_penalty_player_3_left_seconds = ellapsed_time_penalty_player_3_right_seconds
            buffer_ellapsed_time_penalty_player_1_right_seconds = ellapsed_time_penalty_player_1_left_seconds
            buffer_ellapsed_time_penalty_player_2_right_seconds = ellapsed_time_penalty_player_2_left_seconds
            buffer_ellapsed_time_penalty_player_3_right_seconds = ellapsed_time_penalty_player_3_left_seconds

            #ellapsed_time_penalty_player_1_right_seconds = ellapsed_time_penalty_player_1_left_seconds
            #ellapsed_time_penalty_player_1_left_seconds = buffer_ellapsed_time_penalty_player_1_seconds

            #buffer_ellapsed_time_penalty_player_2_seconds = ellapsed_time_penalty_player_2_right_seconds
            #ellapsed_time_penalty_player_2_right_seconds = ellapsed_time_penalty_player_2_left_seconds
            #ellapsed_time_penalty_player_2_left_seconds = buffer_ellapsed_time_penalty_player_2_seconds

            #buffer_ellapsed_time_penalty_player_3_seconds = ellapsed_time_penalty_player_3_right_seconds
            #ellapsed_time_penalty_player_3_right_seconds = ellapsed_time_penalty_player_3_left_seconds
            #ellapsed_time_penalty_player_3_left_seconds = buffer_ellapsed_time_penalty_player_3_seconds

            _buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = \
                buffer_last_started_ellapsed_time_penalty_player_1_left_seconds
            _buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = \
                buffer_last_started_ellapsed_time_penalty_player_2_left_seconds
            _buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = \
                buffer_last_started_ellapsed_time_penalty_player_3_left_seconds

            _buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = \
                buffer_last_started_ellapsed_time_penalty_player_1_right_seconds
            _buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = \
                buffer_last_started_ellapsed_time_penalty_player_2_right_seconds
            _buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = \
                buffer_last_started_ellapsed_time_penalty_player_3_right_seconds
            #buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = \
            #    buffer_last_started_ellapsed_time_penalty_player_1_right_seconds
            #buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = \
            #    _buffer_last_started_ellapsed_time_penalty_player_seconds

            #_buffer_last_started_ellapsed_time_penalty_player_seconds = \
            #    buffer_last_started_ellapsed_time_penalty_player_2_left_seconds
            #buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = \
            #    buffer_last_started_ellapsed_time_penalty_player_2_right_seconds
            #buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = \
            #    _buffer_last_started_ellapsed_time_penalty_player_seconds
            #
            #_buffer_last_started_ellapsed_time_penalty_player_seconds = \
            #    buffer_last_started_ellapsed_time_penalty_player_3_left_seconds
            #buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = \
            #    buffer_last_started_ellapsed_time_penalty_player_3_right_seconds
            #buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = \
            #    _buffer_last_started_ellapsed_time_penalty_player_seconds
            #
            buffer_running_time_penalty_player_1_right = running_time_penalty_player_1_left
            buffer_running_time_penalty_player_2_right = running_time_penalty_player_2_left
            buffer_running_time_penalty_player_3_right = running_time_penalty_player_3_left
            buffer_running_time_penalty_player_1_left = running_time_penalty_player_1_right
            buffer_running_time_penalty_player_2_left = running_time_penalty_player_2_right
            buffer_running_time_penalty_player_3_left = running_time_penalty_player_3_right

            #running_time_penalty_player_1_left = running_time_penalty_player_1_right
            #running_time_penalty_player_1_right = buffer_running_time_penalty_player
            #
            #buffer_running_time_penalty_player = running_time_penalty_player_2_left
            #running_time_penalty_player_2_left = running_time_penalty_player_2_right
            #running_time_penalty_player_2_right = buffer_running_time_penalty_player
            #
            #buffer_running_time_penalty_player = running_time_penalty_player_3_left
            #running_time_penalty_player_3_left = running_time_penalty_player_3_right
            #running_time_penalty_player_3_right = buffer_running_time_penalty_player
            #
            buffer_time_penalty_player_1_right_initialized = time_penalty_player_1_left_initialized
            buffer_time_penalty_player_2_right_initialized = time_penalty_player_2_left_initialized
            buffer_time_penalty_player_3_right_initialized = time_penalty_player_3_left_initialized
            buffer_time_penalty_player_1_left_initialized = time_penalty_player_1_right_initialized
            buffer_time_penalty_player_2_left_initialized = time_penalty_player_2_right_initialized
            buffer_time_penalty_player_3_left_initialized = time_penalty_player_3_right_initialized
            #time_penalty_player_1_left_initialized = time_penalty_player_1_right_initialized
            #time_penalty_player_1_right_initialized = buffer_time_penalty_initialized
            #
            #buffer_time_penalty_initialized = time_penalty_player_2_left_initialized
            #time_penalty_player_2_left_initialized = time_penalty_player_2_right_initialized
            #time_penalty_player_2_right_initialized = buffer_time_penalty_initialized
            #
            #buffer_time_penalty_initialized = time_penalty_player_3_left_initialized
            #time_penalty_player_3_left_initialized = time_penalty_player_3_right_initialized
            #time_penalty_player_3_right_initialized = buffer_time_penalty_initialized

            # dont transfer timepenalty status of the board where the counter is already at zero.
            # for those which counter was >0, then the status should be on "activate"
            _buffer_last_time_start_of_the_timepenalty_player1_left = buffer_last_time_start_of_the_timepenalty_player1_right
            _buffer_last_time_start_of_the_timepenalty_player2_left = buffer_last_time_start_of_the_timepenalty_player2_right
            _buffer_last_time_start_of_the_timepenalty_player3_left = buffer_last_time_start_of_the_timepenalty_player3_right

            _buffer_last_time_start_of_the_timepenalty_player1_right = buffer_last_time_start_of_the_timepenalty_player1_left
            _buffer_last_time_start_of_the_timepenalty_player2_right = buffer_last_time_start_of_the_timepenalty_player2_left
            _buffer_last_time_start_of_the_timepenalty_player3_right = buffer_last_time_start_of_the_timepenalty_player3_left

            # the game was stopped. So, the counters are not changing. However, the counters are a result of timepenalty minus ellapsed time
            # perhaps looking at counter should be avoided but only looking if ellapsed time smaller than timepenalty maxi time
            counter_seconds_time_penalty_player_1_left = buffer_counter_seconds_time_penalty_player_1_left
            counter_seconds_time_penalty_player_2_left = buffer_counter_seconds_time_penalty_player_2_left
            counter_seconds_time_penalty_player_3_left = buffer_counter_seconds_time_penalty_player_3_left
            counter_seconds_time_penalty_player_1_right = buffer_counter_seconds_time_penalty_player_1_right
            counter_seconds_time_penalty_player_2_right = buffer_counter_seconds_time_penalty_player_2_right
            counter_seconds_time_penalty_player_3_right = buffer_counter_seconds_time_penalty_player_3_right

            if counter_seconds_time_penalty_player_1_left > 0:
                self.button_activate_timepenalty_player_1_left.set_active(True)
                # activate the button initialize the data. So, put them at the previous status stored in buffer
                time_penalty_player_1_left_initialized = buffer_time_penalty_player_1_left_initialized
                running_time_penalty_player_1_left = buffer_running_time_penalty_player_1_left
                buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = _buffer_last_started_ellapsed_time_penalty_player_1_left_seconds
                buffer_last_time_start_of_the_timepenalty_player1_left = _buffer_last_time_start_of_the_timepenalty_player1_left
                ellapsed_time_penalty_player_1_left_seconds = buffer_ellapsed_time_penalty_player_1_left_seconds

            else:
                self.clear_time_penalty_entry_player_1_left(self)
                self.button_clear_timepenalty_player_1_left.set_active(True)
            #
            if counter_seconds_time_penalty_player_2_left > 0:
                self.button_activate_timepenalty_player_2_left.set_active(True)
                time_penalty_player_2_left_initialized = buffer_time_penalty_player_2_left_initialized
                running_time_penalty_player_2_left = buffer_running_time_penalty_player_2_left
                buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = _buffer_last_started_ellapsed_time_penalty_player_2_left_seconds
                buffer_last_time_start_of_the_timepenalty_player2_left = _buffer_last_time_start_of_the_timepenalty_player2_left
                ellapsed_time_penalty_player_2_left_seconds = buffer_ellapsed_time_penalty_player_2_left_seconds

            else:
                self.clear_time_penalty_entry_player_2_left(self)
                self.button_clear_timepenalty_player_2_left.set_active(True)
            #
            if counter_seconds_time_penalty_player_3_left > 0:
                self.button_activate_timepenalty_player_3_left.set_active(True)
                time_penalty_player_3_left_initialized = buffer_time_penalty_player_3_left_initialized
                running_time_penalty_player_3_left = buffer_running_time_penalty_player_3_left
                buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = _buffer_last_started_ellapsed_time_penalty_player_3_left_seconds
                buffer_last_time_start_of_the_timepenalty_player3_left = _buffer_last_time_start_of_the_timepenalty_player3_left
                ellapsed_time_penalty_player_3_left_seconds = buffer_ellapsed_time_penalty_player_3_left_seconds

            else:
                self.clear_time_penalty_entry_player_3_left(self)
                self.button_clear_timepenalty_player_3_left.set_active(True)
            #
            if counter_seconds_time_penalty_player_1_right > 0:
                self.button_activate_timepenalty_player_1_right.set_active(True)
                time_penalty_player_1_right_initialized = buffer_time_penalty_player_1_right_initialized
                running_time_penalty_player_1_right = buffer_running_time_penalty_player_1_right
                buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = _buffer_last_started_ellapsed_time_penalty_player_1_right_seconds
                buffer_last_time_start_of_the_timepenalty_player1_right = _buffer_last_time_start_of_the_timepenalty_player1_right
                ellapsed_time_penalty_player_1_right_seconds = buffer_ellapsed_time_penalty_player_1_right_seconds

            else:
                self.clear_time_penalty_entry_player_1_right(self)
                self.button_clear_timepenalty_player_1_right.set_active(True)
            #
            if counter_seconds_time_penalty_player_2_right > 0:
                self.button_activate_timepenalty_player_2_right.set_active(True)
                time_penalty_player_2_right_initialized = buffer_time_penalty_player_2_right_initialized
                running_time_penalty_player_2_right = buffer_running_time_penalty_player_2_right
                buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = _buffer_last_started_ellapsed_time_penalty_player_2_right_seconds
                buffer_last_time_start_of_the_timepenalty_player2_right = _buffer_last_time_start_of_the_timepenalty_player2_right
                ellapsed_time_penalty_player_2_right_seconds = buffer_ellapsed_time_penalty_player_2_right_seconds


            else:
                self.clear_time_penalty_entry_player_2_right(self)
                self.button_clear_timepenalty_player_2_right.set_active(True)
            #
            if counter_seconds_time_penalty_player_3_right > 0:
                self.button_activate_timepenalty_player_3_right.set_active(True)
                time_penalty_player_3_right_initialized = buffer_time_penalty_player_3_right_initialized
                running_time_penalty_player_3_right = buffer_running_time_penalty_player_3_right
                buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = _buffer_last_started_ellapsed_time_penalty_player_3_right_seconds
                buffer_last_time_start_of_the_timepenalty_player3_right = _buffer_last_time_start_of_the_timepenalty_player3_right
                ellapsed_time_penalty_player_3_right_seconds = buffer_ellapsed_time_penalty_player_3_right_seconds


            else:
                self.clear_time_penalty_entry_player_3_right(self)
                self.button_clear_timepenalty_player_3_right.set_active(True)

            # all labels back to black. If any blinking, it will be overtaken by label_update

            self.label_control_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                     gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_1_left.override_color(gtk.StateFlags.NORMAL,
                                                                  gdk.RGBA(0, 0, 0, 1))
            self.label_control_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                     gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_2_left.override_color(gtk.StateFlags.NORMAL,
                                                                  gdk.RGBA(0, 0, 0, 1))
            self.label_control_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                     gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_3_left.override_color(gtk.StateFlags.NORMAL,
                                                                  gdk.RGBA(0, 0, 0, 1))

            self.label_control_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                      gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_1_right.override_color(gtk.StateFlags.NORMAL,
                                                                   gdk.RGBA(0, 0, 0, 1))
            self.label_control_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                      gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_2_right.override_color(gtk.StateFlags.NORMAL,
                                                                   gdk.RGBA(0, 0, 0, 1))
            self.label_control_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                      gdk.RGBA(0, 0, 0, 1))
            self.label_view_time_penalty_player_3_right.override_color(gtk.StateFlags.NORMAL,
                                                                   gdk.RGBA(0, 0, 0, 1))


            #
            # update all labels of timepenalty left. necessary? probably not because the update of the labels is
            # overtaken by the label update method
            #
            if running_time_penalty_player_1_left:
                # necessary? see thread update timers
                m, s = divmod(counter_seconds_time_penalty_player_1_left, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
            else:
                buffer_label_to_appear = "00:00"
            self.label_control_time_penalty_player_1_left.set_text(buffer_label_to_appear)
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_1_right.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_1_left.set_text(buffer_label_to_appear)
            #
            if running_time_penalty_player_2_left:
                m, s = divmod(counter_seconds_time_penalty_player_2_left, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
            else:
                buffer_label_to_appear = "00:00"
            self.label_control_time_penalty_player_2_left.set_text(buffer_label_to_appear)
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_2_right.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_2_left.set_text(buffer_label_to_appear)
            #
            if running_time_penalty_player_3_left:
                m, s = divmod(counter_seconds_time_penalty_player_3_left, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
            else:
                buffer_label_to_appear = "00:00"
            self.label_control_time_penalty_player_3_left.set_text(buffer_label_to_appear)

            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_3_right.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_3_left.set_text(buffer_label_to_appear)
            #
            # update all labels of timepenalty right
            #
            if running_time_penalty_player_1_right:
                m, s = divmod(counter_seconds_time_penalty_player_1_right, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
            else:
                buffer_label_to_appear = "00:00"
            self.label_control_time_penalty_player_1_right.set_text(buffer_label_to_appear)
            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_1_left.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_1_right.set_text(buffer_label_to_appear)
            #
            if running_time_penalty_player_2_right:
                m, s = divmod(counter_seconds_time_penalty_player_2_right, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
            else:
                buffer_label_to_appear = "00:00"
            self.label_control_time_penalty_player_2_right.set_text(buffer_label_to_appear)

            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_2_left.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_2_right.set_text(buffer_label_to_appear)
            #
            if running_time_penalty_player_3_right:
                m, s = divmod(counter_seconds_time_penalty_player_3_right, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
            else:
                buffer_label_to_appear = "00:00"
            self.label_control_time_penalty_player_3_right.set_text(buffer_label_to_appear)

            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_time_penalty_player_3_left.set_text(buffer_label_to_appear)
            else:
                self.label_view_time_penalty_player_3_right.set_text(buffer_label_to_appear)
            #
            #
            # swap points results
            buffer_points_team = int(self.spinbutton_points_team_left.get_value())
            self.spinbutton_points_team_left.set_value(self.spinbutton_points_team_right.get_value())
            self.spinbutton_points_team_right.set_value(buffer_points_team)
            #
            # swap team name
            buffer_team_name = self.label_control_team_name_left.get_text()
            self.label_control_team_name_left.set_text(self.label_control_team_name_right.get_text())
            self.label_control_team_name_right.set_text(str(buffer_team_name))

            if self.button_type_view_invertedcontrolview.get_active() \
                    and self.button_separate_game_view_on.get_active():
                self.label_view_team_name_left.set_text(str(self.label_control_team_name_right.get_text()))
                self.label_view_team_name_right.set_text(str(self.label_control_team_name_left.get_text()))
            else:
                self.label_view_team_name_left.set_text(str(self.label_control_team_name_left.get_text()))
                self.label_view_team_name_right.set_text(str(self.label_control_team_name_right.get_text()))
            #
            # clear timeout number to zero if switch clicked
            #            self.spinbutton_timeout_left.set_value(0)
            #            self.spinbutton_timeout_right.set_value(0)
            #
            # swap team color and team name
            # put the background in blue or white later
            #  https://developer.gnome.org/gdk3/stable/gdk3-RGBA-Colors.html
            if left_team_is_blue:  # change to white
                left_team_is_blue = False
                # left is white background (and black letter)
                self.eventbox_control_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.eventbox_control_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.eventbox_control_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(1, 1, 1, 1))
                self.eventbox_control_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 1, 1))
                self.label_control_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.label_control_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

                self.eventbox_control_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_control_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                self.eventbox_control_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_control_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

                if self.button_type_view_invertedcontrolview.get_active() \
                        and self.button_separate_game_view_on.get_active():
                    self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(1, 1, 1, 1))
                    self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 1, 1))
                    self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                   gdk.RGBA(1, 1, 1, 1))
                    self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 1, 1))
                    self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                    self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                    #
                    self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                gdk.RGBA(0, 0, 1, 1))
                    self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                    self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(1, 1, 1, 1))
                    self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                else:
                    self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(1, 1, 1, 1))
                    self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 1, 1))
                    self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(1, 1, 1, 1))
                    self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                   gdk.RGBA(0, 0, 1, 1))
                    self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                    self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

                    self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                gdk.RGBA(1, 1, 1, 1))
                    self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                    self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 1, 1))
                    self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

            else:
                left_team_is_blue = True
                # left is blue background (and white letter)
                self.eventbox_control_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.eventbox_control_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.eventbox_control_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 1, 1))
                self.eventbox_control_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(1, 1, 1, 1))
                self.label_control_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_control_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                self.eventbox_control_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
                self.label_control_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.eventbox_control_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                self.label_control_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                if self.button_type_view_invertedcontrolview.get_active() \
                        and self.button_separate_game_view_on.get_active():
                    self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 1, 1))
                    self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(1, 1, 1, 1))
                    self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                   gdk.RGBA(0, 0, 1, 1))
                    self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(1, 1, 1, 1))
                    self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                    self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                    self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                gdk.RGBA(1, 1, 1, 1))
                    self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
                    self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 1, 1))
                    self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

                else:
                    self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(0, 0, 1, 1))
                    self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(1, 1, 1, 1))
                    self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                  gdk.RGBA(0, 0, 1, 1))
                    self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                   gdk.RGBA(1, 1, 1, 1))
                    self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                    self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

                    self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL,
                                                                                gdk.RGBA(0, 0, 1, 1))
                    self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
                    self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL,
                                                                                 gdk.RGBA(1, 1, 1, 1))
                    self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))

    #
    #
    ############################################################################################
    # special timeperiod penalty / break / timeout
    #
    def activate_break_mode(self, widget, data=None):
        global break_mode
        global penalty_mode
        global timeout_mode
        global logfile_game
        global ellapsed_time_special_sequence_seconds
        global ellapsed_maximum_time_special_sequence_seconds
        global counter_seconds_special_time_sequence
        global stopped_special_time_sequence
        global running_penalty
        global running_timeout
        global running_break
        '''activate_break_mode'''
        if self.button_special_time_sequence_break.get_active():
            #print("********************************")
            #print("**                            **")
            #print("** try to activate_break_mode **")
            #print("**                            **")
            #print("********************************")
            #
            if running_penalty:
                self.button_special_time_sequence_penalty.set_active(True)
            elif running_break:
                self.button_special_time_sequence_break.set_active(True)
            elif running_timeout:
                self.button_special_time_sequence_timeout.set_active(True)
            else:
                # if nothing is running. If running, it must be stopped before from the GUI
                #print("*************************")
                #print("**                     **")
                #print("** activate_break_mode **")
                #print("**                     **")
                #print("*************************")

                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    logfile_game_handler.write("activate break mode\n")

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "activate break mode\n")

                    logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()


                stopped_special_time_sequence = False
                break_mode = True
                self.label_view_specific_timesequence.set_text("break")
                self.label_view_status_specific_timesequence.set_text("ready")
                penalty_mode = False
                timeout_mode = False
                running_penalty = False
                running_timeout = False
                running_break = False
                ellapsed_time_special_sequence_seconds = 0
                ellapsed_maximum_time_special_sequence_seconds = 60 * int(self.spinbutton_break_time.get_value())
                counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds
                m, s = divmod(counter_seconds_special_time_sequence, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                self.button_stop_special_time_sequence.set_active(True)
            #

    def activate_penalty_mode(self, widget, data=None):
        global break_mode
        global penalty_mode
        global timeout_mode
        global ellapsed_time_special_sequence_seconds
        global ellapsed_maximum_time_special_sequence_seconds
        global counter_seconds_special_time_sequence
        global stopped_special_time_sequence
        global running_penalty
        global running_timeout
        global running_break
        if self.button_special_time_sequence_penalty.get_active():
            #print("***************************")
            #print("**                       **")
            #print("** activate_penalty_mode **")
            #print("**                       **")
            #print("***************************")
            if running_penalty:
                self.button_special_time_sequence_penalty.set_active(True)
            elif running_break:
                self.button_special_time_sequence_break.set_active(True)
            elif running_timeout:
                self.button_special_time_sequence_timeout.set_active(True)
            else:
                # if nothing is running. If running, it must be stopped before

                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    logfile_game_handler.write("activate penalty mode\n")

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "activate penalty mode\n")

                    logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()

                stopped_special_time_sequence = False
                break_mode = False
                penalty_mode = True
                self.label_view_specific_timesequence.set_text("penalty")
                self.label_view_status_specific_timesequence.set_text("ready")
                timeout_mode = False
                running_penalty = False
                running_timeout = False
                running_break = False
                ellapsed_time_special_sequence_seconds = 0
                ellapsed_maximum_time_special_sequence_seconds = int(self.spinbutton_penalty_duration.get_value())
                counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds
                m, s = divmod(counter_seconds_special_time_sequence, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                self.button_stop_special_time_sequence.set_active(True)
            #
            #

    def activate_timeout_mode(self, widget, data=None):
        global break_mode
        global penalty_mode
        global timeout_mode
        global ellapsed_time_special_sequence_seconds
        global ellapsed_maximum_time_special_sequence_seconds
        global counter_seconds_special_time_sequence
        global stopped_special_time_sequence
        global running_penalty
        global running_timeout
        global running_break
        if self.button_special_time_sequence_timeout.get_active():
            #
            #            if ((running_penalty or running_break or running_timeout) and counter_seconds_special_time_sequence <= 0) or \
            #                (not running_penalty and not running_break and not running_timeout):
            #
            if running_penalty:
                self.button_special_time_sequence_penalty.set_active(True)
            elif running_break:
                self.button_special_time_sequence_break.set_active(True)
            elif running_timeout:
                self.button_special_time_sequence_timeout.set_active(True)
            else:
                # if nothing is running. If running, it must be stopped before
                #print("***************************")
                #print("**                       **")
                #print("** activate_timeout_mode **")
                #print("**                       **")
                #print("***************************")

                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    logfile_game_handler.write("activate timeout mode\n")

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "activate timeout mode\n")

                    logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()

                stopped_special_time_sequence = False
                break_mode = False
                penalty_mode = False
                timeout_mode = True
                self.label_view_specific_timesequence.set_text("timeout")
                self.label_view_status_specific_timesequence.set_text("ready")
                running_penalty = False
                running_timeout = False
                running_break = False
                ellapsed_time_special_sequence_seconds = 0
                ellapsed_maximum_time_special_sequence_seconds = 60 * int(self.spinbutton_timeout.get_value())
                counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds
                m, s = divmod(counter_seconds_special_time_sequence, 60)
                buffer_label_to_appear = "%02d:%02d" % (m, s)
                self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                self.button_stop_special_time_sequence.set_active(True)

    #            else:
    #                if running_penalty:
    #                    self.button_special_time_sequence_penalty.set_active(True)
    #                elif running_break:
    #                    self.button_special_time_sequence_break.set_active(True)
    #                else:
    #                    self.button_special_time_sequence_timeout.set_active(True)
    #
    #
    def start_timeperiod_of_game_on_hold(self, widget, data=None):
        global running_penalty
        global running_break
        global running_timeout
        global break_mode
        global penalty_mode
        global timeout_mode
        global buffer_time_start_special_time_sequence
        global ellapsed_special_time_sequence_seconds
        global stopped_special_time_sequence
        #
        if self.button_start_special_time_sequence.get_active() and \
                self.button_special_time_sequence_none.get_active() == False:
            #print("start_timeperiod_of_game_on_hold", counter_seconds_board)
            # can only starts if nothing runs
            now = datetime.now()

#            if self.button_log_functionality_on.get_active():
#                logfile_game_handler = open(logfile_game, 'a')
#                logfile_game_handler.write("************* control board activity **************\n")
#                logfile_game_handler.write("start timeperiod of game on hold\n")
#                logfile_game_handler.write("  at time     : %s\n" % (str(now.strftime("%H:%M:%S"))))
#                logfile_game_handler.write("  at countdown: %s\n" % (self.label_control_current_time.get_text()))
#                logfile_game_handler.write("***************************************************\n")
#                logfile_game_handler.close()


            if not running_penalty and not running_break and not running_timeout:
                stopped_special_time_sequence = False

                if self.button_special_time_sequence_break.get_active():
                    running_penalty = False
                    running_timeout = False
                    running_break = True

                    if self.button_log_functionality_on.get_active():
                        logfile_game_handler = open(logfile_game, 'a')
                        logfile_game_handler.write("************* control board activity **************\n")
                        logfile_game_handler.write("start break time\n")

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "start break time\n")

                        logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))

                        logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                        logfile_game_handler.write("  break duration         : %s s\n" % (str(timeout_maximum_seconds)))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                    "  break duration         : %s s\n" % (str(timeout_maximum_seconds)))

                        logfile_game_handler.write("***************************************************\n")
                        logfile_game_handler.close()

                if self.button_special_time_sequence_timeout.get_active():

                    running_penalty = False
                    running_timeout = True
                    running_break = False

                    if self.button_log_functionality_on.get_active():
                        logfile_game_handler = open(logfile_game, 'a')
                        logfile_game_handler.write("************* control board activity **************\n")
                        logfile_game_handler.write("start timeout\n")

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "start timeout\n")

                        logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                        logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                        logfile_game_handler.write("  timeout duration       : %s s\n" % (str(timeout_maximum_seconds)))

                        logfile_game_handler.write("***************************************************\n")
                        logfile_game_handler.close()

                if self.button_special_time_sequence_penalty.get_active():
                    running_penalty = True
                    running_timeout = False
                    running_break = False

                    if self.button_log_functionality_on.get_active():
                        logfile_game_handler = open(logfile_game, 'a')
                        logfile_game_handler.write("************* control board activity **************\n")
                        logfile_game_handler.write("start penalty\n")

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                              "start penalty\n")

                        logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                        logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                        self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                        logfile_game_handler.write("  penalty duration       : %s s\n" % (str(penalty_maximum_seconds)))

                        logfile_game_handler.write("***************************************************\n")
                        logfile_game_handler.close()

                self.label_view_status_specific_timesequence.set_text("running")
                buffer_time_start_special_time_sequence = datetime.now()
                ellapsed_special_time_sequence_seconds = 0
            #
            #

    def stop_timeperiod_of_game_on_hold(self, widget, data=None):
        global running_penalty
        global running_break
        global running_timeout
        global stopped_special_time_sequence
        global logfile_game
        if self.button_stop_special_time_sequence.get_active():
            #print("stop_timeperiod_of_game_on_hold")
            # stop whatever is running
            stopped_special_time_sequence = True
            now = datetime.now()

            if self.button_log_functionality_on.get_active() and self.button_special_time_sequence_penalty.get_active():
                self.label_penaltylog_dialog_time.set_text(str(penalty_maximum_seconds-ellapsed_special_time_sequence_seconds))
                logfile_game_handler = open(logfile_game, 'a')
                logfile_game_handler.write("************* control board activity **************\n")
                logfile_game_handler.write("stop penalty\n")

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "stop penalty\n")

                logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at penalty countdown   : %s s\n" % (str(penalty_maximum_seconds-ellapsed_special_time_sequence_seconds)))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  at penalty countdown   : %s s\n" % (str(penalty_maximum_seconds-ellapsed_special_time_sequence_seconds)))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()
                self.penaltylogdialog.show()

            if self.button_log_functionality_on.get_active() and self.button_special_time_sequence_break.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                logfile_game_handler.write("************* control board activity **************\n")
                logfile_game_handler.write("stop break\n")

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "stop break\n")

                logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at break countdown     : %s s\n" % (str(break_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                        "  at break countdown     : %s s\n" % (str(break_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()

            if self.button_log_functionality_on.get_active() and self.button_special_time_sequence_timeout.get_active():
                logfile_game_handler = open(logfile_game, 'a')
                logfile_game_handler.write("************* control board activity **************\n")
                logfile_game_handler.write("stop timeout\n")

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                      "stop timeout\n")

                logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                logfile_game_handler.write("  at timeout countdown   : %s s\n" % (str(timeout_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                            "  at timeout countdown   : %s s\n" % (str(timeout_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                logfile_game_handler.write("***************************************************\n")
                logfile_game_handler.close()

            self.label_view_status_specific_timesequence.set_text("stopped")
            running_penalty = False
            running_timeout = False
            running_break = False
        #
        #

    def clearreset_timeperiod_of_game_on_hold(self, widget, data=None):
        global running_penalty
        global running_break
        global running_timeout
        global break_mode
        global penalty_mode
        global timeout_mode
        global counter_seconds_special_time_sequence
        global ellapsed_maximum_time_special_sequence_seconds
        global stopped_special_time_sequence
        global ellapsed_time_special_sequence_seconds
        if self.button_clearreset_special_time_sequence.get_active():
            #
            if ((running_penalty or running_break or running_timeout) and counter_seconds_special_time_sequence > 0):
                self.button_start_special_time_sequence.set_active(True)
            elif ((running_penalty or running_break or running_timeout) and counter_seconds_special_time_sequence <= 0):
                self.button_stop_special_time_sequence.set_active(True)
                break_mode = False
                penalty_mode = False
                timeout_mode = False
                running_penalty = False
                running_timeout = False
                running_break = False
                stopped_special_time_sequence = True
                ellapsed_maximum_time_special_sequence_seconds = 0
                counter_seconds_special_time_sequence = 0
            else:
                #print("******************************************")
                #print("** clear_timeperiod_of_game_on_hold ", counter_seconds_board, " **")
                #print("******************************************")
                # especially important when a penalty is completed by time not zero and the screen has to be resetted
                # button active only nothing separate is running or counter is already at zero
                # put the timeperiod to zero

                if counter_seconds_special_time_sequence <= 0 or \
                        (not running_penalty and not running_break and not running_timeout):
                    stopped_special_time_sequence = True
                    #               counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds ?? to zero!
                    ellapsed_maximum_time_special_sequence_seconds = 0
                    counter_seconds_special_time_sequence = 0
                    #                time.sleep(1) # must be bigger than the time update of the main counter ??
                    #                break_mode = False
                    #                penalty_mode = False
                    #                timeout_mode = False
                    #                running_penalty = False
                    #                running_timeout = False
                    #                running_break = False
                    if self.button_special_time_sequence_break.get_active():
                        #
                #        print("reset_break_mode")
                        stopped_special_time_sequence = False
                        break_mode = True
                        self.label_view_specific_timesequence.set_text("break")
                        self.label_view_status_specific_timesequence.set_text("ready")
                        penalty_mode = False
                        timeout_mode = False
                        running_penalty = False
                        running_timeout = False
                        running_break = False
                        ellapsed_time_special_sequence_seconds = 0
                        ellapsed_maximum_time_special_sequence_seconds = 60 * int(
                            self.spinbutton_break_time.get_value())
                        counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds
                        if self.button_log_functionality_on.get_active():
                            now = datetime.now()
                            logfile_game_handler = open(logfile_game, 'a')
                            logfile_game_handler.write("************* control board activity **************\n")
                            logfile_game_handler.write("reset break\n")

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                  "reset break\n")

                            logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                            logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                  "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                            logfile_game_handler.write("  at break countdown     : %s s\n" % (
                                str(break_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                  "  at break countdown     : %s s\n" % (
                                str(break_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                            logfile_game_handler.write("***************************************************\n")
                            logfile_game_handler.close()

                    if self.button_special_time_sequence_penalty.get_active():
                #        print("reset_penalty_mode")
                        stopped_special_time_sequence = False
                        break_mode = False
                        penalty_mode = True
                        self.label_view_specific_timesequence.set_text("penalty")
                        self.label_view_status_specific_timesequence.set_text("ready")
                        timeout_mode = False
                        running_penalty = False
                        running_timeout = False
                        running_break = False
                        ellapsed_time_special_sequence_seconds = 0
                        ellapsed_maximum_time_special_sequence_seconds = int(
                            self.spinbutton_penalty_duration.get_value())
                        counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds
                        if self.button_log_functionality_on.get_active():
                            now = datetime.now()
                            logfile_game_handler = open(logfile_game, 'a')
                            logfile_game_handler.write("************* control board activity **************\n")
                            logfile_game_handler.write("reset penalty\n")

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                  "reset penalty\n")

                            logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                            logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                  "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                            logfile_game_handler.write("  at penalty countdown   : %s s\n" % (
                                str(penalty_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                            self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                  "  at penalty countdown   : %s s\n" % (
                                str(penalty_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                            logfile_game_handler.write("***************************************************\n")
                            logfile_game_handler.close()

                    if self.button_special_time_sequence_timeout.get_active():
                        if ((
                                    running_penalty or running_break or running_timeout) and counter_seconds_special_time_sequence <= 0) or \
                                (not running_penalty and not running_break and not running_timeout):
                            # if nothing is running. If running, it must be stopped before
                #            print("reset_timeout_mode")
                            stopped_special_time_sequence = False
                            break_mode = False
                            penalty_mode = False
                            timeout_mode = True
                            self.label_view_specific_timesequence.set_text("timeout")
                            self.label_view_status_specific_timesequence.set_text("ready")
                            running_penalty = False
                            running_timeout = False
                            running_break = False
                            ellapsed_time_special_sequence_seconds = 0
                            ellapsed_maximum_time_special_sequence_seconds = 60 * int(
                                self.spinbutton_timeout.get_value())
                            counter_seconds_special_time_sequence = ellapsed_maximum_time_special_sequence_seconds
                            if self.button_log_functionality_on.get_active():
                                now = datetime.now()
                                logfile_game_handler = open(logfile_game, 'a')
                                logfile_game_handler.write("************* control board activity **************\n")
                                logfile_game_handler.write("reset timeout\n")

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                      "reset timeout\n")

                                logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                                logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (
                                self.label_control_current_time.get_text()))

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                      "  at scoreboard countdown: %s min:s\n" % (
                                self.label_control_current_time.get_text()))

                                logfile_game_handler.write("  at timeout countdown   : %s s\n" % (
                                    str(timeout_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                                self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                                      "  at timeout countdown   : %s s\n" % (
                                    str(timeout_maximum_seconds - ellapsed_special_time_sequence_seconds)))

                                logfile_game_handler.write("***************************************************\n")
                                logfile_game_handler.close()
                    #                    else:
                    #                        if running_penalty:
                    #                            self.button_special_time_sequence_penalty.set_active(True)
                    #                        elif running_break:
                    #                            self.button_special_time_sequence_break.set_active(True)
                    #                        else:
                    #                            self.button_special_time_sequence_timeout.set_active(True)

                    #                buffer_label_to_appear = "none"
                    #                self.label_view_specific_timesequence.set_text(buffer_label_to_appear)
                    #                self.label_view_status_specific_timesequence.set_text(buffer_label_to_appear)
                    #
                    #                self.button_special_time_sequence_none.set_active(True)
                    #                self.button_stop_special_time_sequence.set_active(True)
                    #
                    #                buffer_label_to_appear = "00:00"
                    #                self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                    #                self.label_view_special_time_sequence.set_text(buffer_label_to_appear)
                    #
                    m, s = divmod(counter_seconds_special_time_sequence, 60)
                    buffer_label_to_appear = "%02d:%02d" % (m, s)
                    self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
        #
        #

    ############################################################################################
    #
    # function accross all page
    #
    ############################################################################################
    #
    def deactivate_event_mode(self, widget, data=None):
        global stopped_special_time_sequence
        global ellapsed_maximum_time_special_sequence_seconds
        global counter_seconds_special_time_sequence
        global break_mode
        global penalty_mode
        global timeout_mode
        global running_penalty
        global running_break
        global running_timeout
        #
        # deactivate event mode only if something is not running = it must be stopped before a hold action can be done
        if self.button_special_time_sequence_none.get_active():
            if running_penalty:
                self.button_special_time_sequence_penalty.set_active(True)
            elif running_break:
                self.button_special_time_sequence_break.set_active(True)
            elif running_timeout:
                self.button_special_time_sequence_timeout.set_active(True)
            else:
                #print("no special sequence")

                if self.button_log_functionality_on.get_active():
                    logfile_game_handler = open(logfile_game, 'a')
                    now = datetime.now()
                    logfile_game_handler.write("************* control board activity **************\n")
                    logfile_game_handler.write(
                        "deactivate special event\n")

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "deactivate special event\n")

                    logfile_game_handler.write("  at time %s h:min:s\n" % (str(now.strftime("%H:%M:%S"))))
                    logfile_game_handler.write("  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    self.logtext_view.get_buffer().insert(self.logtext_view.get_buffer().get_end_iter(),
                                                          "  at scoreboard countdown: %s min:s\n" % (self.label_control_current_time.get_text()))

                    logfile_game_handler.write("***************************************************\n")
                    logfile_game_handler.close()


                buffer_label_to_appear = "none"
                self.label_view_specific_timesequence.set_text(buffer_label_to_appear)
                self.label_view_status_specific_timesequence.set_text(buffer_label_to_appear)
                buffer_label_to_appear = "none"
                self.label_control_special_time_sequence.set_text(buffer_label_to_appear)
                self.label_view_special_time_sequence.set_text(buffer_label_to_appear)
                if self.button_stop_special_time_sequence.get_active():
                    stopped_special_time_sequence = True
                    ellapsed_maximum_time_special_sequence_seconds = 0
                    counter_seconds_special_time_sequence = 0
                    break_mode = False
                    penalty_mode = False
                    timeout_mode = False
                    running_penalty = False
                    running_timeout = False
                    running_break = False

    def __init__(self):
        global running_period_time
        global left_team_is_blue
        global buffer_time_start_special_time_sequence
        global start_time_of_the_game
        global start_time_control_timepenalty_player1_left
        global start_time_control_timepenalty_player2_left
        global start_time_control_timepenalty_player3_left
        global start_time_control_timepenalty_player1_right
        global start_time_control_timepenalty_player2_right
        global start_time_control_timepenalty_player3_right
        global start_time_of_second_period
        global end_time_of_the_game
        global buffer_last_time_stop
        global buffer_last_time_stop_control_timepenalty_player1_left
        global buffer_last_time_stop_control_timepenalty_player2_left
        global buffer_last_time_stop_control_timepenalty_player3_left
        global buffer_last_time_stop_control_timepenalty_player1_right
        global buffer_last_time_stop_control_timepenalty_player2_right
        global buffer_last_time_stop_control_timepenalty_player3_right
        global buffer_last_time_start
        global buffer_last_time_start_control_timepenalty_player1_left
        global buffer_last_time_start_control_timepenalty_player2_left
        global buffer_last_time_start_control_timepenalty_player3_left
        global buffer_last_time_start_control_timepenalty_player1_right
        global buffer_last_time_start_control_timepenalty_player2_right
        global buffer_last_time_start_control_timepenalty_player3_right
        global ellapsed_period_time_seconds
        global buffer_last_started_ellapsed_period_time_seconds
        global period_time_in_second
        global period_time_in_second_orig
        global counter_seconds_board
        global timepenalty_maximum_seconds
        global penalty_maximum_seconds
        global timeout_maximum_seconds
        global break_maximum_seconds
        global ellapsed_special_time_sequence_seconds
        global counter_seconds_special_time_sequence
        global ellapsed_maximum_time_special_sequence_seconds
        global ellapsed_time_penalty_player_1_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_1_left_seconds
        global counter_seconds_time_penalty_player_1_left
        global ellapsed_time_penalty_player_2_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_2_left_seconds
        global counter_seconds_time_penalty_player_2_left
        global ellapsed_time_penalty_player_3_left_seconds
        global buffer_last_started_ellapsed_time_penalty_player_3_left_seconds
        global counter_seconds_time_penalty_player_3_left
        global ellapsed_time_penalty_player_1_right_seconds
        global buffer_last_started_ellapsed_time_penalty_player_1_right_seconds
        global counter_seconds_time_penalty_player_1_right
        global ellapsed_time_penalty_player_2_right_seconds
        global buffer_last_started_ellapsed_time_penalty_player_2_right_seconds
        global counter_seconds_time_penalty_player_2_right
        global ellapsed_time_penalty_player_3_right_seconds
        global buffer_last_started_ellapsed_time_penalty_player_3_right_seconds
        global counter_seconds_time_penalty_player_3_right
        global activated_time_penalty_player_1_left_to_enter_or_delete
        global activated_time_penalty_player_2_left_to_enter_or_delete
        global activated_time_penalty_player_3_left_to_enter_or_delete
        global activated_time_penalty_player_1_right_to_enter_or_delete
        global activated_time_penalty_player_2_right_to_enter_or_delete
        global activated_time_penalty_player_3_right_to_enter_or_delete
        global time_penalty_player_1_left_initialized
        global time_penalty_player_1_right_initialized
        global time_penalty_player_2_left_initialized
        global time_penalty_player_2_right_initialized
        global time_penalty_player_3_left_initialized
        global time_penalty_player_3_right_initialized
        global game_started
        global action_start_time_of_the_game_is_ACTIVE
        global running_first_period_time
        global running_second_period_time
        global running_penalty
        global running_timeout
        global running_break
        global stopped_special_time_sequence
        global running_time_penalty_player_1_left
        global running_time_penalty_player_2_left
        global running_time_penalty_player_3_left
        global running_time_penalty_player_1_right
        global running_time_penalty_player_2_right
        global running_time_penalty_player_3_right
        global buffer_counter_minutes_time_penalty_player_1
        global buffer_counter_seconds_time_penalty_player_1
        global buffer_counter_minutes_time_penalty_player_2
        global buffer_counter_seconds_time_penalty_player_2
        global buffer_counter_minutes_time_penalty_player_3
        global buffer_counter_seconds_time_penalty_player_3
        global buffer_running_time_penalty_player_1_left
        global buffer_running_time_penalty_player_2_left
        global buffer_running_time_penalty_player_3_left
        global buffer_points_team
        global period_time_default_minutes
        global warning_default_timepenalty
        global warning_timepenalty
        global warning_default_break_timeout
        global warning_break_timeout
        global break_time_default_minutes
        global penalty_duration_default_seconds
        global timeout_default_minutes
        global time_penalty_default_minutes
        global number_of_period
        global watch_stop_default
        global watch_stop
        global now_dont_stop
        global logdata_array
        global add_time_seconds
        global penalty_can_be_activated_from_penaltylogdata
        global penalty_can_be_activated_from_logdata
        #
        # variable definition time
        # all VDST official default times are hard coded here
        period_time_default_minutes = 15  # min  the label in the time view will be 00:00 text min:sec
        warning_default_timepenalty = 10  # blinking of time penalty starts 10s from end
        break_time_default_minutes = 5  # min the label in the time view will be 00:00 text min:sec
        penalty_duration_default_seconds = 45  # s the label in the time view will be 00 text sec
        timeout_default_minutes = 1  # min the label in the time view will be 00:00 text min:sec
        time_penalty_default_minutes = 2  # min the label in the time view will be 00:00 text min:sec
        number_of_period = 2
        watch_stop_default = True
        add_time_seconds = 0
        #
        warning_default_break_timeout = 20  # non VDST data; 20s before end of the timeout or break, it will start
        # to blink in order to inform the referees and players to go into the water and be ready to start the match again

        penalty_can_be_activated_from_penaltylogdata = False
        penalty_can_be_activated_from_logdata = False

        # define all relations between labels and entries and combobox and spinbutton and python variables
        builder = gtk.Builder()
        ############################################################################################
        ############################################################################################
        #
        # modify that link below at a new installation
        #
        ############################################################################################
        #
        builder.add_from_file("/home/family/UWR_scoreboard/scoreboard_uwr.glade")
        #
        ############################################################################################
        ############################################################################################
        #
        self.controlwindow = builder.get_object("scoreboard_control_window")
        self.viewwindow = builder.get_object("scoreboard_view_window")
        self.logdialog = builder.get_object("scoreboard_log_dialog")
        self.penaltylogdialog = builder.get_object("scoreboard_penaltylog_dialog")
        self.logoffdialog = builder.get_object("scoreboard_logoff_confirm")
        self.logcanceldialog = builder.get_object("scoreboard_logcancel_confirm")
        self.resetdialog = builder.get_object("scoreboard_resetconfirm")
        self.exitdialog = builder.get_object("scoreboard_exitconfirm")
        self.logviewwindow = builder.get_object("scoreboard_logview_window")
        #
        # declaration of all data from the "scoreboard_control_window"
        self.spinbutton_points_team_left = builder.get_object("spinbutton_points_team_left")
        self.spinbutton_points_team_right = builder.get_object("spinbutton_points_team_right")
        self.spinbutton_timeout_left = builder.get_object("spinbutton_timeout_left")
        self.spinbutton_timeout_right = builder.get_object("spinbutton_timeout_right")
        self.spinbutton_period_time = builder.get_object("spinbutton_period_time")
        self.spinbutton_period = builder.get_object("spinbutton_period")
        self.spinbutton_break_time = builder.get_object("spinbutton_break_time")
        self.spinbutton_penalty_duration = builder.get_object("spinbutton_penalty_duration")
        self.spinbutton_timeout = builder.get_object("spinbutton_timeout")
        self.spinbutton_time_penalty = builder.get_object("spinbutton_time_penalty")
        self.spinbutton_add_time = builder.get_object("spinbutton_add_time")
        self.spinbutton_warning_timepenalty = builder.get_object("spinbutton_warning_timepenalty")
        self.spinbutton_warning_break_timeout = builder.get_object("spinbutton_warning_break_timeout")
        #
        self.togglebutton_start_stop_game = builder.get_object("togglebutton_start_stop_game")
        #        self.comboboxtext_watch_stop = builder.get_object("comboboxtext_watch_stop")
        self.entry_tournament_name = builder.get_object("entry_tournament_name")
        self.entry_tournament_contact = builder.get_object("entry_tournament_contact")
        self.entry_team_blue_name = builder.get_object("entry_team_blue_name")
        self.entry_team_white_name = builder.get_object("entry_team_white_name")
        self.entry_name_penalty_player_1_left = builder.get_object("entry_name_penalty_player_1_left")
        self.entry_name_penalty_player_2_left = builder.get_object("entry_name_penalty_player_2_left")
        self.entry_name_penalty_player_3_left = builder.get_object("entry_name_penalty_player_3_left")
        self.entry_name_penalty_player_1_right = builder.get_object("entry_name_penalty_player_1_right")
        self.entry_name_penalty_player_2_right = builder.get_object("entry_name_penalty_player_2_right")
        self.entry_name_penalty_player_3_right = builder.get_object("entry_name_penalty_player_3_right")
        # define here further entries
        #
        self.label_control_current_time = builder.get_object("label_control_current_time")
        self.eventbox_control_left = builder.get_object("eventbox_control_left")
        #        self.eventbox_blue_team = builder.get_object("eventbox_blue_team")
        self.label_control_team_name_left = builder.get_object("label_control_team_name_left")
        self.eventbox_control_right = builder.get_object("eventbox_control_right")
        self.label_control_team_name_right = builder.get_object("label_control_team_name_right")
        self.label_control_tournament_name = builder.get_object("label_control_tournament_name")
        self.label_control_tournament_contact = builder.get_object("label_control_tournament_contact")
        self.spinbutton_minutes_time_correction = builder.get_object("spinbutton_minutes_time_correction")
        self.spinbutton_seconds_time_correction = builder.get_object("spinbutton_seconds_time_correction")
        #        self.label_special_time_sequence = builder.get_object("label_special_time_sequence")
        #
        self.label_control_time_penalty_player_1_left = builder.get_object("label_control_time_penalty_player_1_left")
        self.label_control_time_penalty_player_2_left = builder.get_object("label_control_time_penalty_player_2_left")
        self.label_control_time_penalty_player_3_left = builder.get_object("label_control_time_penalty_player_3_left")
        self.label_control_time_penalty_player_1_right = builder.get_object("label_control_time_penalty_player_1_right")
        self.label_control_time_penalty_player_2_right = builder.get_object("label_control_time_penalty_player_2_right")
        self.label_control_time_penalty_player_3_right = builder.get_object("label_control_time_penalty_player_3_right")
        #
        #        self.label_timeout = builder.get_object("label_timeout")
        #        self.label_break = builder.get_object("label_break")
        #        self.label_penalty = builder.get_object("label_penalty")
        #
        #self.spinbutton_points_team_left = builder.get_object("spinbutton_points_team_left")
        #self.spinbutton_points_team_right = builder.get_object("spinbutton_points_team_right")
        self.eventbox_control_points_team_left = builder.get_object("eventbox_control_points_team_left")
        self.eventbox_control_points_team_right = builder.get_object("eventbox_control_points_team_right")
        self.label_control_points_team_left = builder.get_object("label_control_points_team_left")
        self.label_control_points_team_right = builder.get_object("label_control_points_team_right")
        self.label_control_special_time_sequence = builder.get_object("label_control_special_time_sequence")
        self.eventbox_control_team_name_left = builder.get_object("eventbox_control_team_name_left")
        self.eventbox_control_team_name_right = builder.get_object("eventbox_control_team_name_right")
        #
        # declaration of all data from the view window
        self.eventbox_view_team_color_left = builder.get_object("eventbox_view_team_color_left")
        self.eventbox_view_team_color_right = builder.get_object("eventbox_view_team_color_right")
        self.eventbox_view_points_team_left = builder.get_object("eventbox_view_points_team_left")
        self.eventbox_view_points_team_right = builder.get_object("eventbox_view_points_team_right")
        self.label_view_period = builder.get_object("label_view_period")
        self.label_view_current_time = builder.get_object("label_view_current_time")
        self.label_view_points_team_left = builder.get_object("label_view_points_team_left")
        self.label_view_timeout_left = builder.get_object("label_view_timeout_left")
        self.label_view_timeout_right = builder.get_object("label_view_timeout_right")
        self.label_view_points_team_right = builder.get_object("label_view_points_team_right")
        self.eventbox_view_team_color_left = builder.get_object("eventbox_view_team_color_left")
        self.eventbox_view_team_color_right = builder.get_object("eventbox_view_team_color_right")

        self.label_view_team_name_left = builder.get_object("label_view_team_name_left")
        self.label_view_team_name_right = builder.get_object("label_view_team_name_right")
        self.eventbox_view_team_name_left = builder.get_object("eventbox_view_team_name_left")
        self.eventbox_view_team_name_right = builder.get_object("eventbox_view_team_name_right")

        self.label_view_tournament_name = builder.get_object("label_view_tournament_name")
        self.label_view_tournament_contact = builder.get_object("label_view_tournament_contact")
        self.label_view_specific_timesequence = builder.get_object("label_view_specific_timesequence")
        self.label_view_status_specific_timesequence = builder.get_object("label_view_status_specific_timesequence")
        self.label_view_special_time_sequence = builder.get_object("label_view_special_time_sequence")
        self.label_view_time_penalty_player_1_left = builder.get_object("label_view_time_penalty_player_1_left")
        self.label_view_time_penalty_player_2_left = builder.get_object("label_view_time_penalty_player_2_left")
        self.label_view_time_penalty_player_3_left = builder.get_object("label_view_time_penalty_player_3_left")
        self.label_view_time_penalty_player_1_right = builder.get_object("label_view_time_penalty_player_1_right")
        self.label_view_time_penalty_player_2_right = builder.get_object("label_view_time_penalty_player_2_right")
        self.label_view_time_penalty_player_3_right = builder.get_object("label_view_time_penalty_player_3_right")
        #
        self.label_view_name_penalty_player_1_left = builder.get_object("label_view_name_penalty_player_1_left")
        self.label_view_name_penalty_player_2_left = builder.get_object("label_view_name_penalty_player_2_left")
        self.label_view_name_penalty_player_3_left = builder.get_object("label_view_name_penalty_player_3_left")
        self.label_view_name_penalty_player_1_right = builder.get_object("label_view_name_penalty_player_1_right")
        self.label_view_name_penalty_player_2_right = builder.get_object("label_view_name_penalty_player_2_right")
        self.label_view_name_penalty_player_3_right = builder.get_object("label_view_name_penalty_player_3_right")
        #
        self.button_blue_starts_left = builder.get_object("button_blue_starts_left")
        self.button_blue_starts_right = builder.get_object("button_blue_starts_right")
        self.button_type_view_invertedcontrolview = builder.get_object("button_type_view_invertedcontrolview")
        self.button_type_view_copycontrolview = builder.get_object("button_type_view_copycontrolview")
        self.button_separate_game_view_off = builder.get_object("button_separate_game_view_off")
        self.button_separate_game_view_on = builder.get_object("button_separate_game_view_on")
        self.button_log_functionality_off = builder.get_object("button_log_functionality_off")
        self.button_log_functionality_on = builder.get_object("button_log_functionality_on")
        self.button_logview_hide = builder.get_object("button_logview_hide")
        self.button_logview_pn = builder.get_object("button_logview_on")
        self.logtext_view = builder.get_object("logtext_view") # GtkTextView
        self.entry_log_filename = builder.get_object("entry_log_filename")
        self.button_nostop_watch = builder.get_object("button_nostop_watch")
        self.button_stop_watch = builder.get_object("button_stop_watch")
        self.button_activate_timepenalty_player_1_left = builder.get_object("button_activate_timepenalty_player_1_left")
        self.button_activate_timepenalty_player_2_left = builder.get_object("button_activate_timepenalty_player_2_left")
        self.button_activate_timepenalty_player_3_left = builder.get_object("button_activate_timepenalty_player_3_left")
        self.button_activate_timepenalty_player_1_right = builder.get_object(
            "button_activate_timepenalty_player_1_right")
        self.button_activate_timepenalty_player_2_right = builder.get_object(
            "button_activate_timepenalty_player_2_right")
        self.button_activate_timepenalty_player_3_right = builder.get_object(
            "button_activate_timepenalty_player_3_right")
        self.button_clear_timepenalty_player_1_left = builder.get_object("button_clear_timepenalty_player_1_left")
        self.button_clear_timepenalty_player_2_left = builder.get_object("button_clear_timepenalty_player_2_left")
        self.button_clear_timepenalty_player_3_left = builder.get_object("button_clear_timepenalty_player_3_left")
        self.button_clear_timepenalty_player_1_right = builder.get_object("button_clear_timepenalty_player_1_right")
        self.button_clear_timepenalty_player_2_right = builder.get_object("button_clear_timepenalty_player_2_right")
        self.button_clear_timepenalty_player_3_right = builder.get_object("button_clear_timepenalty_player_3_right")
        self.button_stop_special_time_sequence = builder.get_object("button_stop_special_time_sequence")
        self.button_start_special_time_sequence = builder.get_object("button_start_special_time_sequence")
        self.button_clearreset_special_time_sequence = builder.get_object("button_clearreset_special_time_sequence")
        self.button_special_time_sequence_none = builder.get_object("button_special_time_sequence_none")
        self.button_special_time_sequence_timeout = builder.get_object("button_special_time_sequence_timeout")
        self.button_special_time_sequence_break = builder.get_object("button_special_time_sequence_break")
        self.button_special_time_sequence_penalty = builder.get_object("button_special_time_sequence_penalty")
        #
        self.ChooserButton_read_file_settings = builder.get_object("ChooserButton_read_file_settings")
        #
        self.label_log_dialog_time = builder.get_object("label_log_dialog_time")
        self.label_log_dialog_message =  builder.get_object("label_log_dialog_message")
        self.entry_log_dialog_remark_referee = builder.get_object("entry_log_dialog_remark_referee")
        self.entry_log_dialog_remark_scripter = builder.get_object("entry_log_dialog_remark_scripter")
        self.label_penaltylog_dialog_time = builder.get_object("label_penaltylog_dialog_time")
        self.label_penaltylog_dialog_message = builder.get_object("label_penaltylog_dialog_message")
        self.entry_penaltylog_dialog_remark_referee = builder.get_object("entry_penaltylog_dialog_remark_referee")
        self.entry_penaltylog_dialog_remark_scripter = builder.get_object("entry_penaltylog_dialog_remark_scripter")

        ##################################
        #   INIT the matrix of all data inputs
        #
        col = 14
        row = 10
        logdata_array = [[""] * col for _ in range(row)]
        #neutralarrayline = ["","","","","","","","","","","","","",""]
        #logdata_array = []
        #for i in range(9):
        #    logdata_array.append(neutralarrayline)

        self.entry_logarray = []
        for i in range(10):
            self.entry_logarray.append([])
            for j in range(14):
                self.entry_logarray[i].append([])
                self.entry_logarray[i][j] = builder.get_object(str('%(prefix)s%(line)02d_%(column)02d'%{'prefix': "ld", 'line': i, 'column': j}))
        #        self.entry_logarray[i][j].set_name(str('%(prefix)s%(line)02d_%(column)02d'%{'prefix': "ld", 'line': i, 'column': j}))

        ##################################
        #   INIT the matrix of all penalty inputs
        #
        self.entry_penaltylogarray = []
        for i in range(10):
            self.entry_penaltylogarray.append([])
            for j in range(12):
                self.entry_penaltylogarray[i].append([])
                self.entry_penaltylogarray[i][j] = builder.get_object(str(
                            '%(prefix)s%(line)02d_%(column)02d' % {'prefix': "lp", 'line': i, 'column': j}))
        #        self.entry_penaltylogarray[i][j].set_name(str(
        #            '%(prefix)s%(line)02d_%(column)02d' % {'prefix': "lp", 'line': i, 'column': j}))


        ##################################
        #self.entry_log_dialog_remark_equipment = builder.get_object("entry_log_dialog_remark_equipment")
        self.entry_anytime_line1intolog = builder.get_object("entry_anytime_line1intolog")
        self.entry_anytime_line2intolog = builder.get_object("entry_anytime_line2intolog")

        self.eventbox_exitbutton = builder.get_object("eventbox_exitbutton")
        self.eventbox_resetbutton = builder.get_object("eventbox_resetbutton")

        self.button_exit_view_window = builder.get_object("button_exit_view_window")
        #
        # connect all signals to actions
        builder.connect_signals(self)

        for i in range(10):
            for j in range(14):
                if j!=13 and j!=2:
                    self.entry_logarray[i][j].connect("toggled", self.checklogdata,str(
                    '%(prefix)s%(line)02d_%(column)02d' % {'prefix': "ld", 'line': i, 'column': j}))

        for i in range(10):
            for j in range(12):
                if j!=11 and j!=2:
                    self.entry_penaltylogarray[i][j].connect("toggled", self.checkpenaltylogdata,str(
                    '%(prefix)s%(line)02d_%(column)02d' % {'prefix': "lp", 'line': i, 'column': j}))

        thread_time_control.connect("update_timers", self.update_timer_labels)
        #
        #        GDK_Escape = 0xff1b
        buffer_time_start_special_time_sequence = datetime.now()
        #
        # datetime data useful for elapsed time calculation and later for log / protocol
        start_time_of_the_game = datetime.now()
        start_time_control_timepenalty_player1_left = datetime.now()
        start_time_control_timepenalty_player2_left = datetime.now()
        start_time_control_timepenalty_player3_left = datetime.now()
        start_time_control_timepenalty_player1_right = datetime.now()
        start_time_control_timepenalty_player2_right = datetime.now()
        start_time_control_timepenalty_player3_right = datetime.now()
        start_time_of_second_period = datetime.now()
        end_time_of_the_game = datetime.now()  # usefull for log / protocol
        # for running time calculation of the main time counting
        buffer_last_time_stop = datetime.now()
        buffer_last_time_stop_control_timepenalty_player1_left = datetime.now()
        buffer_last_time_stop_control_timepenalty_player2_left = datetime.now()
        buffer_last_time_stop_control_timepenalty_player3_left = datetime.now()
        buffer_last_time_stop_control_timepenalty_player1_right = datetime.now()
        buffer_last_time_stop_control_timepenalty_player2_right = datetime.now()
        buffer_last_time_stop_control_timepenalty_player3_right = datetime.now()
        buffer_last_time_start = datetime.now()
        buffer_last_time_start_control_timepenalty_player1_left = datetime.now()
        buffer_last_time_start_control_timepenalty_player2_left = datetime.now()
        buffer_last_time_start_control_timepenalty_player3_left = datetime.now()
        buffer_last_time_start_control_timepenalty_player1_right = datetime.now()
        buffer_last_time_start_control_timepenalty_player2_right = datetime.now()
        buffer_last_time_start_control_timepenalty_player3_right = datetime.now()
        #
        # SEVERAL global parameters and stopwatches to be defined
        #       FIRST for period time downcounting
        #       SECOND for special_time_sequence
        #       3 for the time penalty players left
        #       3 for the time penalty players right
        #
        ellapsed_period_time_seconds = 0
        buffer_last_started_ellapsed_period_time_seconds = 0
        period_time_in_second = 15 * 60
        period_time_in_second_orig = 15*60
        counter_seconds_board = 15 * 60
        warning_timepenalty = warning_default_timepenalty
        warning_break_timeout = warning_default_break_timeout
        watch_stop = True
        now_dont_stop = False
        #
        # diverse parameter of special_time_sequence
        timepenalty_maximum_seconds = 120
        penalty_maximum_seconds = 45
        timeout_maximum_seconds = 1 * 60
        break_maximum_seconds = 300
        ellapsed_special_time_sequence_seconds = 0
        counter_seconds_special_time_sequence = 0
        ellapsed_maximum_time_special_sequence_seconds = 300
        #
        ellapsed_time_penalty_player_1_left_seconds = 0
        buffer_last_started_ellapsed_time_penalty_player_1_left_seconds = 0
        counter_seconds_time_penalty_player_1_left = 0
        #
        ellapsed_time_penalty_player_2_left_seconds = 0
        buffer_last_started_ellapsed_time_penalty_player_2_left_seconds = 0
        counter_seconds_time_penalty_player_2_left = 0
        #
        ellapsed_time_penalty_player_3_left_seconds = 0
        buffer_last_started_ellapsed_time_penalty_player_3_left_seconds = 0
        counter_seconds_time_penalty_player_3_left = 0
        #
        ellapsed_time_penalty_player_1_right_seconds = 0
        buffer_last_started_ellapsed_time_penalty_player_1_right_seconds = 0
        counter_seconds_time_penalty_player_1_right = 0
        #
        ellapsed_time_penalty_player_2_right_seconds = 0
        buffer_last_started_ellapsed_time_penalty_player_2_right_seconds = 0
        counter_seconds_time_penalty_player_2_right = 0
        #
        ellapsed_time_penalty_player_3_right_seconds = 0
        buffer_last_started_ellapsed_time_penalty_player_3_right_seconds = 0
        counter_seconds_time_penalty_player_3_right = 0
        #
        activated_time_penalty_player_1_left_to_enter_or_delete = False
        activated_time_penalty_player_2_left_to_enter_or_delete = False
        activated_time_penalty_player_3_left_to_enter_or_delete = False
        activated_time_penalty_player_1_right_to_enter_or_delete = False
        activated_time_penalty_player_2_right_to_enter_or_delete = False
        activated_time_penalty_player_3_right_to_enter_or_delete = False
        #
        time_penalty_player_1_left_initialized = False
        time_penalty_player_1_right_initialized = False
        time_penalty_player_2_left_initialized = False
        time_penalty_player_2_right_initialized = False
        time_penalty_player_3_left_initialized = False
        time_penalty_player_3_right_initialized = False
        #
        # diverse helpfull match status or timing
        game_started = False
        action_start_time_of_the_game_is_ACTIVE = False  # toggle button start / stop of the overall timing
        running_period_time = False
        running_first_period_time = False
        running_second_period_time = False
        running_penalty = False
        running_timeout = False
        running_break = False
        stopped_special_time_sequence = False
        # basic setup of team name
        left_team_is_blue = True  # at application start
        #
        running_time_penalty_player_1_left = False
        running_time_penalty_player_2_left = False
        running_time_penalty_player_3_left = False
        running_time_penalty_player_1_right = False
        running_time_penalty_player_2_right = False
        running_time_penalty_player_3_right = False
        #
        # buffer for switching the results from right to left in the score viewer
        buffer_counter_minutes_time_penalty_player_1 = 0
        buffer_counter_seconds_time_penalty_player_1 = 0
        buffer_counter_minutes_time_penalty_player_2 = 0
        buffer_counter_seconds_time_penalty_player_2 = 0
        buffer_counter_minutes_time_penalty_player_3 = 0
        buffer_counter_seconds_time_penalty_player_3 = 0
        buffer_running_time_penalty_player_1_left = False
        buffer_running_time_penalty_player_2_left = False
        buffer_running_time_penalty_player_3_left = False
        buffer_points_team = 0
        ################################
        # right is white background (and black letter)
        self.eventbox_control_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        self.eventbox_view_team_color_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        # right point area white
        self.eventbox_control_points_team_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        self.eventbox_view_points_team_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        self.eventbox_control_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        self.eventbox_view_team_name_right.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        # right letters of points black in white team
        self.label_control_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
        self.label_view_points_team_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
        self.label_control_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
        self.label_view_team_name_right.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 0, 1))
        #
        # left point area blue
        self.eventbox_control_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
        self.eventbox_view_team_color_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
        self.eventbox_control_points_team_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
        self.eventbox_view_points_team_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
        # left letters of points white in blue team
        self.label_control_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        self.label_view_points_team_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))

        self.eventbox_control_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
        self.eventbox_view_team_name_left.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(0, 0, 1, 1))
        self.label_control_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        self.label_view_team_name_left.override_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 1, 1, 1))
        #
        #
        self.entry_tournament_name.set_text("tournament")
        self.label_control_tournament_name.set_text("tournament")
        self.label_view_tournament_name.set_text("tournament")
        #
        self.entry_tournament_contact.set_text("Ms./Mr.")
        self.label_control_tournament_contact.set_text("Ms./Mr.")
        self.label_view_tournament_contact.set_text("Ms./Mr.")
        #
        self.entry_team_blue_name.set_text("TeamBLUE")
        self.label_control_team_name_left.set_text("TeamBLUE")
        self.label_view_team_name_left.set_text("Team BLUE")
        #
        self.entry_team_white_name.set_text("TeamWHITE")
        self.label_control_team_name_right.set_text("TeamWHITE")
        self.label_view_team_name_right.set_text("Team WHITE")
        #
        # make exit button for red
        self.eventbox_exitbutton.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 0, 0, 1))
        #
        # orange https://en.wikipedia.org/wiki/X11_color_names test rgb  100%  65%  0%
        self.eventbox_resetbutton.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 0.65, 0, 1))
        # make reset button for red
        # self.eventbox_resetbutton.override_background_color(gtk.StateFlags.NORMAL, gdk.RGBA(1, 0, 0, 1))
        self.label_control_special_time_sequence.set_text("none")
        self.label_view_special_time_sequence.set_text("none")
        #
        style_provider = gtk.CssProvider()
        ############################################################################################
        ############################################################################################
        #
        # modify that link below at a new installation
        #
        ############################################################################################
        css = open('/home/family/UWR_scoreboard/scoreboard_gui_styles.css',
                   'rb')  # rb needed for python 3 support
        ############################################################################################
        ############################################################################################
        css_data = css.read()
        css.close()
        style_provider.load_from_data(css_data)
        gtk.StyleContext.add_provider_for_screen(gdk.Screen.get_default(), style_provider,
                                                 gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


if __name__ == "__main__":
    print("***********************************************************")
    print("*       scoreboard UWR                                    *")
    print("*       underwaterrugby game control and reporting        *")
    print("*       pascaldagornet@yahoo.de                           *")
    print("***********************************************************")
    GUI = GUIclass()
    GUI.controlwindow.show()
    gtk.main()
