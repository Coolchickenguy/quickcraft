import * as fs from "fs";
import * as path from "path";
/**
 *
 * @private
 * @param {Array<Array<string> | {"path":string,"contents":cont}>} cont
 * @returns { Array<Array<string> | {"path":string,"contents":cont}> }
 */
export const dirMap = (cont) =>
  cont.map((val) =>
    fs.statSync(val).isDirectory()
      ? {
          path: val,
          contents: dirMap(
            fs.readdirSync(val).map((valueInner) => path.join(val, valueInner))
          ),
        }
      : val
  );
/**
 * @description Get a directory map of a path
 * @param { string } path
 * @returns { Array<Array<string> | {"path":string,"contents":recusive}>}
 */
export default (path) => dirMap(fs.readdirSync(path));
/**
 *
 * @param { Array<string> } cont
 * @param { string } pathof
 * @returns { Array<string> }
 */
const flatdm = (cont, pathof) =>
  cont
    .map((val) =>
      fs.statSync(path.resolve(pathof, val)).isDirectory()
        ? [
            val,
            ...flatdm(
              fs
                .readdirSync(path.resolve(pathof, val))
                .map((valueInner) => path.join(val, valueInner)),
              pathof
            ),
          ]
        : val
    )
    .flat(1);
/**
 *
 * @param { string } pathof
 * @returns { Array<string> } An array contaning all of the paths
 */
export const dirMapFlat = (pathof) => flatdm(fs.readdirSync(pathof), pathof);
/**
 * A directory map
 * @typedef {Array<Array<string> | {"path":string,"contents":dirmapping}>} dirmapping
 * */