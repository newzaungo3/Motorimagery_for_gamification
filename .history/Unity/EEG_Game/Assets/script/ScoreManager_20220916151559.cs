using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using static Position;

public class ScoreManager : MonoBehaviour
{
    // Start is called before the first frame update
    public TextMeshProUGUI leftScore_text;
    public TextMeshProUGUI rightScore_text;

    private static int leftScore = 0;
    private static int rightScore = 0;
    void Start()
    {
        //leftScore_text.text = "Hello World";
    }

    // Update is called once per frame
    void Update()
    {
        scoreUpdate();
    }
    
    public static void scoreUpdate()
    {
        string decision = "";
        int point =0;
        decision = Position.getPos();
        if (decision == "left")
        {
            leftScore = leftScore + 1;
            point = leftScore;
            leftScore_text.text = point.ToString();
        }
        else if (decision == "right")
        {
            rightScore = rightScore + 1;
            point = rightScore;
            rightScore_text.text = point.ToString();

        }
    }
}