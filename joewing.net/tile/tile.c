/* Tile 20000117 by Joe Wingbermuehle */

#include <gtk/gtk.h>
#include <time.h>
#include <stdlib.h>

/* Functions */
void ButtonClicked(GtkWidget*,gpointer);
int CheckButton(int,int);
void CheckGameOver(void);
void StartGame(int);
void SetButton(int,int);
int GetButton(int);
void NewGame(GtkWidget*,gpointer);
void SetSize3(GtkWidget*,gpointer);
void SetSize4(GtkWidget*,gpointer);
void SetSize5(GtkWidget*,gpointer);
void CreateButtons(void);
void About(void);
void GameOver(void);
int IsPossible(void);
void DestroyMessage(GtkWidget*,gpointer);
void RemoveMessageGrab(GtkWidget*,gpointer);

/* The menus */
static GtkItemFactoryEntry menuItems[]= {
	{ "/_Game",		NULL,		NULL,		0,	"<Branch>" },
	{ "/Game/_New Game",	"<control>N",	NewGame,	0,	NULL },
	{ "/Game/E_xit",	"<control>X",	gtk_main_quit,	0,	NULL },
	{ "/_Size",		NULL,		NULL,		0,	"<Branch>" },
	{ "/Size/  _3  ",	NULL,		SetSize3,	0,	NULL },
	{ "/Size/  _4  ",	NULL,		SetSize4,	0,	NULL },
	{ "/Size/  _5  ",	NULL,		SetSize5,	0,	NULL },
	{ "/_Help",		NULL,		NULL,		0,	"<LastBranch>" },
	{ "/Help/_About",	NULL,		About,		0,	NULL }};
gint menuSize=sizeof(menuItems)/sizeof(menuItems[0]);

/* Gobal variables */
GtkWidget *barray[5*5],*table,*box,*window;
int boardsize;
const int TIMES_TO_SCRAMBLE=100;

/* main */
int main(int argc, char *argv[]) {
	GtkWidget *menubar;
	GtkItemFactory *menu;
	GtkAccelGroup *accelGroup;

	gtk_init(&argc, &argv);

	/* Create window */
	window=gtk_window_new(GTK_WINDOW_TOPLEVEL);
	gtk_window_set_title(GTK_WINDOW(window), "Tile");

	box=gtk_vbox_new(FALSE,1);
	gtk_container_border_width(GTK_CONTAINER(box),1);
	gtk_container_add(GTK_CONTAINER(window),box);
	gtk_widget_show(box);

	accelGroup=gtk_accel_group_new();
	menu=gtk_item_factory_new(GTK_TYPE_MENU_BAR,"<main>",accelGroup);
	gtk_item_factory_create_items(menu,menuSize,menuItems,NULL);
	gtk_window_add_accel_group(GTK_WINDOW(window),accelGroup);
	menubar=gtk_item_factory_get_widget(menu,"<main>");
	gtk_box_pack_start(GTK_BOX(box),menubar,FALSE,TRUE,0);
	gtk_widget_show(menubar);
	
	gtk_signal_connect_object(GTK_OBJECT(window), "delete_event", GTK_SIGNAL_FUNC(gtk_main_quit), NULL);
	gtk_container_set_border_width(GTK_CONTAINER(window), 1);

	StartGame(0);

	gtk_widget_show(window);
	gtk_main();
	return(0);
} /* main */

/* Check if the puzzle is possible */
int IsPossible(void) {
	int x,y;
	int inversions=0;
	int values[boardsize*boardsize];
	for(y=x=0;x<boardsize*boardsize;x++)
		if(GetButton(x)) values[y++]=GetButton(x);

	for(x=0;x<boardsize*boardsize-1;x++) {
		for(y=x+1;y<boardsize*boardsize-1;y++) {
			if(values[y]<values[x]) {
				++inversions;
			}
		}
	}
	if(boardsize%2)
		return 1-(inversions%2);
	else
		return inversions%2;
}

void DisplayMessage(char *s) {
	GtkWidget *dialog, *message, *button;
	dialog=gtk_dialog_new();
	gtk_window_set_title(GTK_WINDOW(dialog),"Tile");
	message=gtk_label_new(s);
	button=gtk_button_new_with_label("OK");
	gtk_signal_connect(GTK_OBJECT(dialog),"destroy",GTK_SIGNAL_FUNC(RemoveMessageGrab),NULL);
	gtk_signal_connect(GTK_OBJECT(button),"clicked",GTK_SIGNAL_FUNC(DestroyMessage),dialog);
	gtk_container_border_width(GTK_CONTAINER(dialog),5);
	gtk_box_pack_start(GTK_BOX(GTK_DIALOG(dialog)->action_area),button,TRUE,TRUE,0);
	gtk_box_pack_start(GTK_BOX(GTK_DIALOG(dialog)->vbox),message,TRUE,TRUE,0);
	gtk_widget_show(message);
	gtk_widget_show(button);
	gtk_widget_show(dialog);
	gtk_grab_add(dialog);
}

void DestroyMessage(GtkWidget *widget,gpointer data) {
	GtkWidget *dialog=(GtkWidget*)(data);
	RemoveMessageGrab(dialog,0);
	gtk_widget_destroy(dialog);
}

void RemoveMessageGrab(GtkWidget *dialog,gpointer data) {
	gtk_grab_remove(dialog);
}

/* Display the about box */
void About(void) {
	DisplayMessage("Tile 20000915\nby Joe Wingbermuehle");
} /* About */

/* Display game over message */
void GameOver(void) {
	DisplayMessage("   You Won!   ");
} /* GameOver */

/* Draw the buttons */
void CreateButtons(void) {
	int x,y;
	char name[]="      ";
	if(boardsize) {
		gtk_widget_destroy(table);
	} else {
		boardsize=3;
	}
	table=gtk_table_new(boardsize,boardsize,TRUE);
	gtk_container_add(GTK_CONTAINER(box),table);
	for(x=0;x<boardsize;x++) {
		for(y=0;y<boardsize;y++) {
			barray[y*boardsize+x]=gtk_button_new_with_label(name);
			gtk_signal_connect(GTK_OBJECT(barray[y*boardsize+x]), "clicked", GTK_SIGNAL_FUNC(ButtonClicked), NULL);
			gtk_table_attach_defaults(GTK_TABLE(table), barray[y*boardsize+x], x, x+1, y, y+1);
			gtk_widget_show(barray[y*boardsize+x]);
		}
	}
	gtk_widget_show(table);
} /* CreateButtons */

/* Start a new game because user says so */
void NewGame(GtkWidget* item, gpointer data) {
	StartGame(boardsize);
} /* NewGame */

/* Set the size of the board and restart */
void SetSize3(GtkWidget* item, gpointer data) {
	StartGame(3);
} /* SetSize3 */

void SetSize4(GtkWidget* item, gpointer data) {
	StartGame(4);
} /* SetSize4 */

void SetSize5(GtkWidget* item, gpointer data) {
	StartGame(5);
} /* SetSize5 */

/* A button was clicked... */
void ButtonClicked(GtkWidget* button, gpointer data) {
	int index;
	gchar *old, *current;

	/* Make index equal the clicked button's position */
	gtk_label_get((GtkLabel*)(GTK_BIN(button)->child),&old);
	for(index=0;;index++) {
		gtk_label_get((GtkLabel*)(GTK_BIN(barray[index])->child),&current);
		if(old[2]==current[2] && old[3]==current[3]) break;
	}

	/* If not on left, check left */
	if(index%boardsize) {
		if(CheckButton(index,index-1)) return;
	}
	/* If not on right, check right */
	if(index%boardsize < boardsize-1) {
		if(CheckButton(index,index+1)) return;
	}
	/* If not on the top, check top */
	if(index/boardsize) {
		if(CheckButton(index,index-boardsize)) return;
	}
	/* If not on the bottom, check bottom */
	if(index/boardsize < boardsize-1) {
		if(CheckButton(index,index+boardsize)) return;
	}
} /* ButtonClicked */

/* Check if a button is near an empty button, swap if so */
int CheckButton(int a, int b) {
/* IN: a=selected button, b=button to check */
/* OUT: returns 1 if empty button found and swaps the buttons */
	int first, second;
	first=GetButton(a);
	second=GetButton(b);
	if(!second) {
		SetButton(a,second);
		SetButton(b,first);
		CheckGameOver();
		return(1);
	}
	return(0);
} /* CheckButton */

/* Check if game over */
void CheckGameOver(void) {
	int index;
	for(index=1;index<boardsize*boardsize;index++)
		if(GetButton(index-1) != index) return;
	/* Game is over */
	GameOver();
	StartGame(boardsize);
} /* CheckGameOver */

/* Start a new game */
void StartGame(int s) {
	int index,value;
	int x,y;
	char used[5*5];
	if(boardsize) boardsize=s;
	CreateButtons();
	srand(time(0));
	do {
		for(x=0;x<boardsize*boardsize;used[x++]=0);
		for(x=0;x<boardsize*boardsize;x++) {
			do {
				y=rand()%(boardsize*boardsize);
			} while(used[y]);
			used[y]=1;
			SetButton(x,y);
		}
	} while(!IsPossible());
} /* StartGame */

/* Set button text */
void SetButton(int index, int value) {
	char text[]="      ";
	if(value>9) {
		text[2]=value/10+'0';
		text[3]=value%10+'0';
	} else {
		if(value) text[3]=value+'0';
	}
	gtk_label_set_text((GtkLabel*)(GTK_BIN(barray[index])->child),text);
} /* SetButton */

/* Get button text */
int GetButton(int index) {
	char *text,value;
	gtk_label_get((GtkLabel*)(GTK_BIN(barray[index])->child),&text);
	if(text[2]==' ')
		if(text[3]!=' ')
			value=text[3]-'0';
		else
			value=0;
	else
		value=(text[2]-'0')*10+text[3]-'0';
	return(value);
} /* GetButton */

