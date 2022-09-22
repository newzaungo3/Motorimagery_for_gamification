using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using static Position;

public class Move : MonoBehaviour
{
    // Start is called before the first frame update
    static string pos = "";
    GameObject cube;
    Vector3 pos = new Vector3(-1.54f,-0.49f,0);
    Vector3 startPos = new Vector3(-1.54f,-0.49f,0);
    void Start()
    {
    }

    // Update is called once per frame
    void Update()
    {
        Debug.Log("Position "+  Position.getPos());
    }
}
