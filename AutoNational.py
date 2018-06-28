import os
import time


def rssFeeds():

    try:
        print("Running Ary News")
        os.system('python Ary.py')
    except:
        print("Issues occured in Ary")  # Testing and Debugging done
        pass

    try:
        print("Running DailyTimes")
        os.system('python DailyTimes.py')    # Testing and Debugging done
    except:
        print("Issues occured in DailyTimes")
        pass

    try:
        print("Running georss")
        os.system('python georss.py')  # Testing and Debugging done
    except:
        print("Issues occured in georss")
        pass

    try:
        print("Running SamaaNews")
        os.system('python SamaaNews.py')     # Testing and Debugging done
    except:
        print("Issues occured in SamaaNews")
        pass

    try:
        print("Running TheNews")
        os.system('python TheNews.py')  # Testing and Debugging done
    except:
        print("Issues occured in TheNews")
        pass

    try:
        print("Running WaqtNews")
        os.system('python WaqtNews.py')     # Testing and Debugging done
    except:
        print("Issues occured in WaqtNews")
        pass

    try:
        print("Running abtak")
        os.system('python abtak.py')    # Testing and Debugging done
    except:
        print("Issues occured in abtak")
        pass

    try:
        print("Running ExpressTribune")
        os.system('python ExpressTribune.py')    # Testing and Debugging done
    except:
        print("Issues occured in ExpressTribune")
        pass

    try:
        print("Running NawaiWaqt")
        os.system('python NawaiWaqt.py')
    except:
        print("Issues occured in NawaiWaqt")
        pass

    try:
        print("Running SuchTv")
        os.system('python SuchTv.py')   # Testing and Debugging done
    except:
        print("Issues occured in SuchTv")
        pass

    try:
        print("Running The Nation News")
        os.system('python Nation.py')   # Testing and Debugging Done
    except:
        print("Issues occured in The Nation News")
        pass

    try:
        print("Running Dunya News")
        os.system('python DuniaNews.py')   # Testing and Debugging Done
    except:
        print("Issues occured in Dunya News")
        pass

    try:
        print("Running Dawn News English")
        os.system('python DawnEng.py')   # Testing and Debugging Done
    except:
        print("Issues occured in Dawn News English")
        pass

    try:
        print("Running Dawn News Urdu")
        os.system('python DawnUrdu.py')   # Testing and Debugging Done
    except:
        print("Issues occured in Dawn News Urdu")
        pass

    try:
        print("Running Aaj News")
        os.system('python AajNews.py')   # Testing and Debugging Done
    except:
        print("Issues occured in Aaj News")
        pass

    try:
        print("Running 92 News")
        os.system('python 92News.py')   # Testing and Debugging Done
    except:
        print("Issues occured in 92 News")
        pass

    try:
        print("Running 24 News HD")
        os.system('python 24NewsHd.py')   # Testing and Debugging Done
    except:
        print("Issues occured in 24 News HD")
        pass

    # URDU POINT is Not considered as an authentic source
    # try:
    #     print("Running Urdu Point")
    #     os.system('python UrduPoint.py')   # Testing and Debugging Done
    # except:
    #     print("Issues occured in Urdu Point")
    #     pass

    try:
        print("Running Roze TV")
        os.system('python RozeTV.py')   # Testing and Debugging Done
    except:
        print("Issues occured in Roze TV")
        pass


while True:
    rssFeeds()
    time.sleep(10)
