using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static sendPosition;

public class GameController : MonoBehaviour
{   
    public Position position;
    // Url: http://localhost/CustomObjectReturnMethodWithQuery?code=1111&msg=wow_it_is_so_cool
    // change {port} to the port set on your UnityHttpController component
    public ReturnResult JoyController(string msg)
    {

        sendPosition.setPos(msg);
        ReturnResult result = new ReturnResult
        {
            msg = msg
        };
        return result;
    }

    //Mark as Serializable to make Unity's JsonUtility works.
    [System.Serializable]
    public class ReturnResult
    {
        public string msg;
    }

}
