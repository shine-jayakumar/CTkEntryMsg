
# CTkEntryMsg - CTkEntry widget with message functionality
#
# CTkEntryMsg class provides a CTkEntry widget with provision to add 
# short information, warning, and error messages below the widget.
# Version: v.0.0.1
# Author: Shine Jayakumar
# License: MIT

from customtkinter import CTkLabel, CTkEntry, CTkFrame
from dataclasses import dataclass
from typing import Callable


@dataclass
class Msg():
    type_: str
    msg: str
    timeout: int | None = None

@dataclass
class Color():
    warn: str
    error: str
    default: str = ''


class CTkEntryMsg(CTkFrame):

    def __init__(
            self, 
            master: any, 
            default_msg: str = '', 
            msg_default_color: str = '#000000',
            msg_warn_color: str = '#FC8309',
            msg_error_color: str = '#FC0909',
            msg_font: tuple = ('Arial', 12),
            highlight: bool = True,
            highlight_warn_color: str = '#FAC36A',
            highlight_error_color: str = '#FF9090',
            msg_timeout: int = 3000,
            *args, **kwargs):
        """ CTkEntry widget with message functionality

        CTkEntryMsg class provides a CTkEntry widget with provision to add 
        short information, warning, and error messages below the widget.

        Args:
            master (any): root, tkinter.Frame or CTkFrame
            default_msg (str, optional): default message. Defaults to ''.
            msg_default_color (str, optional): text color for default message. Defaults to '#000000'.
            msg_warn_color (str, optional): text color for a warning message. Defaults to '#FF9E00'.
            msg_error_color (str, optional): text color for an error message. Defaults to '#F70D0D'.
            msg_font (tuple, optional): font for message. Defaults to ('Arial', 12)
            highlight (bool, optional): change the background for CTkEntry for warnings, error. Defaults to True.
            highlight_warn_fgcolor (str, optional): background color for warnings. Defaults to '#FAC36A'.
            highlight_error_fgcolor (str, optional): background color for errors. Defaults to '#FD8C8C'.
            msg_timeout (int, optional): time in milliseconds to show warnings and errors for. Defaults to 3000 ms.
        """
        super().__init__(master)
        self.configure(
            width = kwargs.get('width', 198) + 2, # defaults to 200 px if width not specified
            height = kwargs.get('width', 28) + 5, # defaults to 30 px if width not specified
            fg_color = 'transparent'
        )
        
        self._default_msg: str = default_msg
        self._msg_color: Color = Color(warn=msg_warn_color, error=msg_error_color, default=msg_default_color)
        self._msg_font: tuple = msg_font

        self._highlight_color: Color = Color(warn=highlight_warn_color, error=highlight_error_color) 
        self._highlight: bool = highlight
        
        self._msg_timeout: int = msg_timeout

        self._msg_queue: list[tuple] = []

        self._entry = CTkEntry(master=self, *args, **kwargs)
        self._entry.grid(row=0, column=0, sticky='ne')

        self._msg = CTkLabel(self, text=self._default_msg)
        self._msg.configure(
            text = self._default_msg, 
            text_color = self._msg_color.default, 
            font=self._msg_font
        )
        if self._default_msg:
            self._msg.grid(row=1, column=0, sticky='ne', padx=(0,5))
        
        # entry box default foreground and text color
        self._default_fgcolor: str = self._entry.cget('fg_color') if \
            not kwargs.get('fg_color', None) else kwargs.get('fg_color', '#FFFFFF')
        self._default_text_color: str = self._entry.cget('text_color') if \
            not kwargs.get('text_color', None) else kwargs.get('text_color', '#000000')

        # Adding CTkEntry public methods to the CTkEntryMsg class
        ctkentry_funcs = [funcname for funcname in vars(CTkEntry).keys() 
                          if not funcname.startswith('_') and funcname != 'configure'] # skip private methods
        for funcname in ctkentry_funcs:
            setattr(self, funcname, getattr(self._entry, funcname))
    
        def _configure(*args, **kwargs):
            if 'fg_color' in kwargs:
                self._default_fgcolor = kwargs.get('fg_color')
            if 'text_color' in kwargs:
                self._default_text_color = kwargs.get('text_color')
            self._entry.configure(*args, **kwargs)

        setattr(self, 'configure', _configure) # self.configure = _configure

    def _restore_msg(self):
        """ Restores message to default state """
        self._msg.configure(
            text = self._default_msg, 
            text_color = self._msg_color.default, 
            font=self._msg_font
        )
        if not self._default_msg:
            self._msg.grid_forget()

    def _restore_entry(self):
        """ Restores entry to default state """
        self._entry.configure(fg_color = self._default_fgcolor, text_color=self._default_text_color)

    def _restore_state(self, persist_msg: bool = False, persist_highlight: bool = False):
        """ Restores message label and entry """
        if not persist_msg:
            self._restore_msg()

        if not persist_highlight and self._highlight:
            self._restore_entry()

    def _msg_queue_showerror(self, msg: Msg, callback: Callable | None = None) -> None:
        """Show error method with custom callback

        Args:
            msg (tuple): message tuple (msg_type, msg, timeout)
            timeout (int | None, optional): error message timeout. This overrides msg_timeout parameter. Defaults to None.
            callback (Callable | None): custom callback method to call after timeout. Defaults to _restore_state()
        """
        if self._highlight:
            self._entry.configure(fg_color = self._highlight_color.error)
        self._msg.configure(text = msg.msg, text_color = self._msg_color.error, anchor='ne', font=self._msg_font)
        self._msg.grid(row=1, column=0, sticky='ne', padx=(0,5), pady=(5,0))
        self._msg.after(msg.timeout if msg.timeout else self._msg_timeout, callback)
    
    def _msg_queue_showwarn(self, msg: Msg, callback: Callable | None = None) -> None:
        """Show warning method with custom callback

        Args:
            msg (tuple): message tuple
            timeout (int | None, optional): warning message timeout. This overrides msg_timeout parameter. Defaults to None.
            callback (Callable | None): custom callback method to call after timeout. Defaults to _restore_state()
        """
        if self._highlight:
            self._entry.configure(fg_color = self._highlight_color.warn)
        self._msg.configure(text = msg.msg, text_color = self._msg_color.warn, anchor='ne', font=self._msg_font)
        self._msg.grid(row=1, column=0, sticky='ne', padx=(0,5), pady=(5,0))
        self._msg.after(msg.timeout if msg.timeout else self._msg_timeout, callback)

    def _get_msg_from_queue(self) -> Msg:
        """ Returns a message from message queue """
        msg = None
        try:
            msg = self._msg_queue.pop(0) # return a message from start of the queue (fifo)
        except IndexError:
            return None
        return msg
    
    def _process_msg_queue(self) -> None:
        
        msg = self._get_msg_from_queue()
        if not msg: # no more messages in queue
            self._restore_state()
            return
    
        if msg.type_.strip() == 'error':
            self._msg_queue_showerror(msg, callback = self._process_msg_queue)
        elif msg.type_.strip() == 'warn':
            self._msg_queue_showwarn(msg, callback = self._process_msg_queue)
        else:
            raise Exception(f'Invalid message type received: {msg.type_}')

    def restore_msg(self):
        """ Restores message to default state """
        self._restore_msg()
    
    def restore_entry(self):
        """ Restores entry to default state """
        self._restore_entry()    

    def showerror(self, msg: str, persist_msg: bool = False, persist_highlight: bool = False, timeout: int|None = None) -> None:
        """Show error message

        Args:
            msg (str): error message
            persist_msg (bool, optional): persist error message after timeout. Defaults to False.
            persist_highlight (bool, optional): persist entry highlight after timeout. Defaults to False.
            timeout (int | None, optional): error message timeout. This overrides msg_timeout parameter. Defaults to None.
        """
        if self._highlight:
            self._entry.configure(fg_color = self._highlight_color.error)
        self._msg.configure(text = msg, text_color = self._msg_color.error, anchor='ne', font=self._msg_font)
        self._msg.grid(row=1, column=0, sticky='ne', padx=(0,5), pady=(5,0))
        self._msg.after(timeout if timeout else self._msg_timeout, lambda: self._restore_state(persist_msg, persist_highlight))

    def showwarn(self, msg: str, persist_msg: bool = False, persist_highlight: bool = False, timeout: int|None = None) -> None:
        """Show warning message

        Args:
            msg (str): warning message
            persist_msg (bool, optional): persist warning message after timeout. Defaults to False.
            persist_highlight (bool, optional): persist entry highlight after timeout. Defaults to False.
            timeout (int | None, optional): warning message timeout. This overrides msg_timeout parameter. Defaults to None.
        """
        if self._highlight:
            self._entry.configure(fg_color = self._highlight_color.warn)
        self._msg.configure(text = msg, text_color = self._msg_color.warn, anchor='ne', font=self._msg_font)
        self._msg.grid(row=1, column=0, sticky='ne', padx=(0,5), pady=(5,0))
        self._msg.after(timeout if timeout else self._msg_timeout, lambda: self._restore_state(persist_msg, persist_highlight))

    def msg_queue(self, messages: list[tuple]) -> None:
        """Chain multiple messages

        Args:
            messages (list[tuple]): list of message tuples [(msg_type: str, msg: str, timeout: int | None),...]
                                    example: 
                                        [('error', 'Username cannot be blank', 2000), ('warning', 'Username same as previous', None)]
        """
        self._msg_queue.extend([Msg(*msg) for msg in messages])
        self._process_msg_queue()
